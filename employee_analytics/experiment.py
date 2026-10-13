"""Run both prompting modes; persist each actual response immediately."""
import argparse
from datetime import datetime, timezone
import json
import math
import time
from pathlib import Path
from .app import ask
from .cases import CASES
from .client import Client
from .database import DB_PATH, ROOT, initialize, query


def equivalent(actual, expected):
    """Compare unordered multisets, ignoring aliases but preserving column order."""
    if actual is None or actual['truncated'] or expected['truncated']:
        return False
    unmatched = list(expected['rows'])
    def cell_equal(a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-5)
        return a == b
    for row in actual['rows']:
        match = next((i for i, other in enumerate(unmatched)
                      if len(row) == len(other) and all(cell_equal(a,b) for a,b in zip(row,other))), None)
        if match is None:
            return False
        unmatched.pop(match)
    return not unmatched


def usage_summary(record, pricing):
    usages = [c['usage'] for c in record['calls']]
    prompt = sum(u.get('prompt_tokens', 0) for u in usages)
    completion = sum(u.get('completion_tokens', 0) for u in usages)
    estimate = None if not pricing else prompt * float(pricing['prompt']) + completion * float(pricing['completion'])
    reported = sum(float(u['cost']) for u in usages) if usages and all(u.get('cost') is not None for u in usages) else None
    return {'prompt_tokens': prompt, 'completion_tokens': completion,
            'estimated_cost_usd': estimate, 'reported_cost_usd': reported}


def write_report(records, path, metadata):
    cases = metadata.get('cases', CASES[:metadata.get('limit', len(CASES))])
    sql_count = sum(case['sql'] is not None for case in cases)
    unsupported_count = len(cases) - sql_count
    lines = ['# Live Prompting Experiment', '',
             f"Run time (UTC): {metadata['started_at']}", '',
             f"Requested model: `{metadata['model']}`. Temperature: 0. Seed database: 30 fictional employees.", '',
             'Zero-shot and few-shot use the same schema, value samples, model, and held-out questions. '
             'Few-shot adds four employee question/SQL examples. No automatic SQL retries or repairs are used.', '',
             'Correctness compares query result multisets with reference SQL, ignoring row order and aliases. '
             'Column order matters, numbers allow small rounding differences. Natural-language answers require manual review; '
             'these are observed results on one small database, not a general model benchmark.', '',
             f'| Strategy | Correct SQL / {sql_count} | Unsupported recognized / {unsupported_count} | Completed / {len(cases)} | Errors |',
             '|---|---|---|---|---|']
    for strategy in ('zero-shot', 'few-shot'):
        subset = [r for r in records if r['strategy'] == strategy]
        count = sum(r['correct'] for r in subset if r['reference_sql'] is not None)
        unsupported = sum(r['correct'] for r in subset if r['reference_sql'] is None)
        lines.append(f"| {strategy} | {count} | {unsupported} | {len(subset)} | {sum(r['status']=='error' for r in subset)} |")
    total_est = sum(r['usage_summary']['estimated_cost_usd'] or 0 for r in records)
    costs = [r['usage_summary']['reported_cost_usd'] for r in records]
    lines += ['', f'Input tokens: {sum(r["usage_summary"]["prompt_tokens"] for r in records)}. '
              f'Output tokens: {sum(r["usage_summary"]["completion_tokens"] for r in records)}.', '',
              f'Estimated cost using catalog rates: ${total_est:.6f}.' if metadata['pricing'] else 'Catalog pricing unavailable; estimated cost is unknown.', '',
              f'API-reported cost: ${sum(costs):.6f}.' if costs and all(c is not None for c in costs) else 'Complete API-reported cost unavailable.', '',
              'Pricing snapshot: `' + json.dumps(metadata['pricing']) + '` (USD per token; estimates do not account for caching or provider differences).', '']
    sql_failures = [r for r in records if r['reference_sql'] is not None and not r['correct']]
    if not sql_failures:
        lines += ['No incorrect SQL results were observed among completed cases. Cases with no reference SQL are scored separately as unsupported questions.', '']
    for r in records:
        lines += [f"## {r['strategy']} / {r['case_id']}", '', r['question'], '',
                  f"Correct: {r['correct']}; status: {r['status']}", '',
                  '```sql', r['sql'] or '-- No SQL generated', '```', '',
                  'Answer: ' + (r['answer'] or '(none)'), '']
        if r['error']:
            lines += ['Error: ' + r['error'], '']
        lines += ['Returned data:', '', '```json', json.dumps(r['results'], indent=2), '```', '']
        if not r['correct']:
            lines += ['Expected data:', '', '```json', json.dumps(r['expected'], indent=2), '```', '']
    path.write_text('\n'.join(lines))


def validate_cases(cases):
    if not cases:
        raise ValueError('Add at least one case to cases.py.')
    ids = set()
    for case in cases:
        if not isinstance(case.get('id'), str) or not case['id'].strip() or case['id'] in ids:
            raise ValueError('Case IDs must be nonempty, unique strings.')
        ids.add(case['id'])
        if not isinstance(case.get('question'), str) or not case['question'].strip():
            raise ValueError(f"Case {case['id']} needs a question.")
        sql = case.get('sql')
        if sql is not None and (not isinstance(sql, str) or not sql.strip()):
            raise ValueError(f"Case {case['id']} needs reference SQL or None for unsupported questions.")


def run_experiment(client, cases, directory, on_update=None):
    """Shared single-model runner; callbacks can refresh a comparison page."""
    validate_cases(cases)
    if not DB_PATH.exists():
        initialize()
    expected = {case['id']: query(case['sql']) if case['sql'] is not None else None for case in cases}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / 'examples.jsonl'
    if output.exists():
        raise ValueError('Results already exist; choose a new --output directory to preserve evidence.')
    metadata = {'started_at': datetime.now(timezone.utc).isoformat(), 'model': client.model,
                'pricing': client.pricing(), 'limit': len(cases), 'cases': cases}
    (directory / 'run.json').write_text(json.dumps(metadata, indent=2))
    records = []
    with output.open('x') as stream:
        for strategy in ('zero-shot', 'few-shot'):
            for case in cases:
                print(f"Running {strategy}: {case['id']}", flush=True)
                started = time.monotonic()
                record = ask(client, case['question'], strategy)
                record['elapsed_seconds'] = time.monotonic() - started
                record['case_id'] = case['id']
                record['reference_sql'] = case['sql']
                record['expected'] = expected[case['id']]
                record['correct'] = (record['status'] == 'unsupported' if case['sql'] is None
                                     else equivalent(record['results'], record['expected']))
                record['usage_summary'] = usage_summary(record, metadata['pricing'])
                stream.write(json.dumps(record) + '\n')
                stream.flush()
                records.append(record)
                write_report(records, directory / 'report.md', metadata)
                if on_update:
                    on_update(records, metadata)
                print(f"  {record['status']}; correct={record['correct']}", flush=True)
                if record['error'] and 'OpenRouter' in record['error']:
                    metadata['error'] = record['error']
                    (directory / 'run.json').write_text(json.dumps(metadata, indent=2))
                    if on_update:
                        on_update(records, metadata)
                    return records, metadata
    print(f"Saved {len(records)} observations to {directory}")
    return records, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model')
    parser.add_argument('--output', default=str(ROOT / 'results'))
    parser.add_argument('--limit', type=int, default=len(CASES), choices=range(1, len(CASES)+1))
    args = parser.parse_args()
    _, metadata = run_experiment(Client(args.model), CASES[:args.limit], args.output)
    if metadata.get('error'):
        raise SystemExit(metadata['error'])


if __name__ == '__main__':
    main()

