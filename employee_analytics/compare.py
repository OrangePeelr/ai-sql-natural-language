"""Compare editable model selections and generate a standalone HTML page."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from .cases import CASES
from .client import Client
from .database import ROOT
from .experiment import run_experiment, validate_cases
from .html_report import write_html
from .models import MODELS


def validate_models(models):
    if not models or any(not isinstance(m, str) or not m.strip() for m in models):
        raise ValueError('Add at least one nonempty model ID to models.py or --models.')
    if len(set(models)) != len(models):
        raise ValueError('Model IDs must be unique.')


def save_comparison(comparison, directory):
    (directory / 'comparison.json').write_text(json.dumps(comparison, indent=2))
    write_html(comparison, directory / 'index.html')


def run_comparison(models, cases, directory, client_factory=Client):
    validate_models(models)
    validate_cases(cases)
    directory = Path(directory)
    # Never mix a new selection with old runs or overwrite their evidence.
    directory.mkdir(parents=True, exist_ok=False)
    comparison = {'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'running',
                  'cases': cases, 'runs': [
                      {'model': model, 'directory': f'{i+1:02d}-' + re.sub(r'[^a-zA-Z0-9_-]', '-', model),
                       'records': [], 'metadata': None, 'error': None} for i, model in enumerate(models)]}
    save_comparison(comparison, directory)
    for run in comparison['runs']:
        print(f"\n=== {run['model']} ===", flush=True)
        def on_update(records, metadata):
            run['records'] = records
            run['metadata'] = metadata
            run['error'] = metadata.get('error')
            save_comparison(comparison, directory)
        try:
            records, metadata = run_experiment(client_factory(run['model']), cases,
                                               directory / run['directory'], on_update)
            on_update(records, metadata)
        except (ValueError, RuntimeError, TimeoutError) as exc:
            run['error'] = str(exc)
            save_comparison(comparison, directory)
            print(f"Model run stopped: {exc}", flush=True)
    comparison['status'] = 'finished with errors' if any(r['error'] for r in comparison['runs']) else 'finished'
    save_comparison(comparison, directory)
    print(f'\nOpen {directory / "index.html"}', flush=True)
    return comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', nargs='+', help='Override the list in employee_analytics/models.py')
    parser.add_argument('--limit', type=int, default=len(CASES), choices=range(1, len(CASES)+1))
    parser.add_argument('--output', type=Path, help='New results directory; defaults to a timestamped folder')
    parser.add_argument('--render-only', type=Path, metavar='RUN_DIRECTORY',
                        help='Rebuild HTML from an existing comparison.json without API calls')
    args = parser.parse_args()
    if args.render_only:
        comparison = json.loads((args.render_only / 'comparison.json').read_text())
        write_html(comparison, args.render_only / 'index.html')
        print(f'Updated {args.render_only / "index.html"}; no API calls.')
        return
    directory = args.output or ROOT / 'results' / 'comparisons' / datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    run_comparison(args.models if args.models is not None else MODELS, CASES[:args.limit], directory)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
