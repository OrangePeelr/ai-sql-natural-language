"""Standalone HTML comparison page, safe to open locally without a server."""
from html import escape
import json

STRATEGIES = ('zero-shot', 'few-shot')


def text(value):
    return escape(str(value), quote=True)


def outcome(record):
    if record is None:
        return 'pending'
    if record['status'] == 'error':
        return 'error'
    return 'pass' if record['correct'] else 'fail'


def write_html(comparison, path):
    cases = comparison['cases']
    runs = comparison['runs']
    sql_total = sum(c['sql'] is not None for c in cases)
    unsupported_total = len(cases) - sql_total
    observations = sum(len(run['records']) for run in runs)
    total = len(runs) * len(STRATEGIES) * len(cases)
    page = [HEAD, '<main><header><p class="eyebrow">EMPLOYEE ANALYTICS / MODEL LAB</p>',
            '<h1>How well do models query your data?</h1>',
            '<p class="intro">The same questions, database, and prompts. Compare results, then inspect the SQL behind each answer.</p>',
            f'<p class="timestamp">Started {text(comparison["started_at"])} · {text(comparison["status"])}</p></header>',
            '<section class="stats" aria-label="Run overview">',
            f'<div><strong>{len(runs)}</strong><span>Models</span></div>',
            f'<div><strong>{len(cases)}</strong><span>Questions per strategy</span></div>',
            f'<div><strong>{observations} / {total}</strong><span>Completed observations</span></div>',
            '</section><section class="panel"><h2>Model comparison</h2>',
            f'<p>{sql_total} SQL questions and {unsupported_total} unsupported questions per strategy. '
            'Scores use reference query results; they do not grade natural-language answers. Pending cases remain visible.</p>',
            '<div class="scroll"><table><thead><tr><th>Model</th><th>Strategy</th><th>Correct SQL</th>'
            '<th>Unsupported recognized</th><th>Completed</th><th>Errors</th><th>Tokens</th><th>Reported cost</th></tr></thead><tbody>']
    for index, run in enumerate(runs):
        for strategy in STRATEGIES:
            records = [r for r in run['records'] if r['strategy'] == strategy]
            correct = sum(r['correct'] for r in records if r['reference_sql'] is not None)
            unsupported = sum(r['correct'] for r in records if r['reference_sql'] is None)
            errors = sum(r['status'] == 'error' for r in records)
            tokens = sum(r['usage_summary']['prompt_tokens'] + r['usage_summary']['completion_tokens'] for r in records)
            costs = [r['usage_summary']['reported_cost_usd'] for r in records]
            cost = f'${sum(costs):.6f}' if costs and all(c is not None for c in costs) else 'Unavailable'
            percent = round(100 * correct / sql_total) if sql_total else 0
            page += [f'<tr><th scope="row">{text(run["model"])}</th><td>{strategy}</td>',
                     f'<td><strong>{correct}/{sql_total}</strong><div class="bar"><i style="width:{percent}%"></i></div></td>',
                     f'<td>{unsupported}/{unsupported_total}</td><td>{len(records)}/{len(cases)}</td>',
                     f'<td>{errors}</td><td>{tokens:,}</td><td>{cost}</td></tr>']
        if run.get('error'):
            page += [f'<tr><td colspan="8" class="error">Run stopped: {text(run["error"])}</td></tr>']
    page += ['</tbody></table></div><p class="footnote">Cost is the API-reported total for recorded calls. '
             'Unavailable means at least one observation has no reported cost. Calls that fail before returning usage may still be billed. '
             'Models can skip the answer call when declining a question; cost totals may reflect different call counts.</p></section>',
             '<section class="panel"><h2>Question outcomes</h2><p>Select an outcome to inspect its evidence.</p>',
             '<div class="filters"><label>Model<select id="model-filter"><option value="">All models</option>']
    for index, run in enumerate(runs):
        page += [f'<option value="m{index}">{text(run["model"])}</option>']
    page += ['</select></label><label>Strategy<select id="strategy-filter"><option value="">Both strategies</option>'
             '<option>zero-shot</option><option>few-shot</option></select></label>',
             '<label>Search questions<input id="search" type="search" placeholder="e.g. salary or hierarchy"></label>',
             '<label class="check"><input id="failures" type="checkbox">Failures and errors only</label></div>',
             '<div class="scroll"><table class="matrix"><thead><tr><th>Question</th>']
    columns = [(i, run, strategy) for i, run in enumerate(runs) for strategy in STRATEGIES]
    lookups = [{(r['case_id'], r['strategy']): r for r in run['records']} for run in runs]
    for i, run, strategy in columns:
        page += [f'<th data-model="m{i}" data-strategy="{strategy}">{text(run["model"])}<small>{strategy}</small></th>']
    page += ['</tr></thead><tbody>']
    details = []
    for j, case in enumerate(cases):
        row_statuses = [outcome(lookups[i].get((case['id'], strategy))) for i, _, strategy in columns]
        page += [f'<tr class="question-row" data-search="{text(case["id"] + " " + case["question"])}">',
                 f'<th scope="row">{text(case["question"])}<small>{text(case["id"])} · '
                 f'{"SQL" if case["sql"] is not None else "Unsupported"}</small></th>']
        for column, (i, run, strategy) in enumerate(columns):
            record = lookups[i].get((case['id'], strategy))
            state = row_statuses[column]
            anchor = f'evidence-{i}-{j}-{strategy}'
            page += [f'<td data-model="m{i}" data-strategy="{strategy}" data-outcome="{state}">']
            badge = f'<span class="badge {state}">{state.capitalize()}</span>'
            page += [f'<a href="#{anchor}">{badge}</a>' if record else badge, '</td>']
            if record:
                attrs = (f'id="{anchor}" data-model="m{i}" data-strategy="{strategy}" '
                         f'data-outcome="{state}" data-search="{text(case["id"] + " " + case["question"])}"')
                details += [f'<details class="evidence" {attrs}><summary>{badge} '
                            f'{text(case["question"])}<small>{text(run["model"])} · {strategy}</small></summary>',
                            '<div class="evidence-body"><h3>Generated SQL</h3>',
                            f'<pre>{text(record["sql"] or "No SQL generated")}</pre><h3>Answer</h3>',
                            f'<div class="answer">{text(record["answer"] or "No answer")}</div>']
                if record['error']:
                    details += [f'<p class="error">{text(record["error"])}</p>']
                details += ['<div class="results-grid"><div><h3>Returned data</h3>',
                            f'<pre>{text(json.dumps(record["results"], indent=2))}</pre></div>',
                            '<div><h3>Reference SQL and expected data</h3>',
                            f'<pre>{text(record["reference_sql"] or "Expected: decline unsupported question")}</pre>',
                            f'<pre>{text(json.dumps(record["expected"], indent=2))}</pre></div></div>',
                            f'<p class="footnote">Actual responding models: {text(", ".join(dict.fromkeys(c["model"] for c in record["calls"])) or "No successful calls")}</p>',
                            f'<pre>{text(json.dumps(record["usage_summary"], indent=2))}</pre>',
                            '</div></details>']
        page += ['</tr>']
    page += ['</tbody></table></div></section><section class="panel"><h2>Query evidence</h2>', *details,
             '</section><footer>Local report · no external scripts or services · '
             'Results reflect this database and this run. Reload the file to see updates during a live comparison.</footer></main>', SCRIPT, '</body></html>']
    path.write_text('\n'.join(page), encoding='utf-8')


HEAD = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Employee Analytics · Model Comparison</title>
<style>
:root{color-scheme:light;--ink:#152538;--muted:#627086;--line:#dae2eb;--blue:#2759b9;--green:#12694e;--red:#ad3146}
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:var(--ink);font:15px/1.6 system-ui,sans-serif}
main{max-width:1440px;margin:auto;padding:48px 28px}header{max-width:900px}.eyebrow{font-size:12px;font-weight:750;letter-spacing:2px;color:var(--blue)}
h1{font-size:clamp(30px,4vw,46px);line-height:1.15;letter-spacing:-1.5px;margin:18px 0}h2{font-size:23px;line-height:1.3;margin:0 0 10px}h3{font-size:14px;margin:20px 0 8px}
.intro{font-size:18px;color:var(--muted)}.timestamp,.footnote,footer{color:var(--muted);font-size:12px}.stats{display:flex;gap:16px;margin:30px 0}
.stats>div{flex:1;background:#e8eef8;border-radius:14px;padding:20px}.stats strong{display:block;font-size:30px;color:var(--blue)}.stats span{color:var(--muted);font-size:13px}
.panel{background:white;padding:26px;border:1px solid var(--line);border-radius:16px;margin:22px 0}.panel>p{color:var(--muted)}
.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;padding:14px;border-bottom:1px solid var(--line);vertical-align:top}thead th{background:#f4f7fb;font-size:12px;color:var(--muted)}
tbody th{font-weight:600}small{display:block;color:var(--muted);font-size:11px;font-weight:400;margin-top:5px}.bar{height:4px;background:#e7edf6;margin-top:8px;min-width:70px;border-radius:5px}.bar i{display:block;height:100%;background:var(--blue);border-radius:5px}
.matrix th:first-child{min-width:250px;max-width:330px}.matrix td{white-space:nowrap}.filters{display:flex;flex-wrap:wrap;gap:16px;margin:22px 0}.filters label{font-size:12px;color:var(--muted)}select,input[type=search]{display:block;margin-top:5px;border:1px solid #bdcbdc;border-radius:7px;background:white;color:var(--ink);padding:10px;max-width:300px}
.check{align-self:end;padding-bottom:10px}.badge{display:inline-block;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:700}.pass{background:#e2f3eb;color:var(--green)}.fail,.badge.error{background:#ffe6eb;color:var(--red)}.pending{background:#edf0f5;color:var(--muted)}.error{color:var(--red)}a{color:var(--blue)}
.evidence{border:1px solid var(--line);border-radius:10px;margin:12px 0;scroll-margin-top:20px}.evidence summary{padding:16px;cursor:pointer;font-weight:600}.evidence-body{padding:0 20px 20px}.results-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;min-width:0}.results-grid>div{min-width:0}
pre{font:12px/1.6 ui-monospace,monospace;background:#f2f5fa;padding:16px;border-radius:8px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}.answer{white-space:pre-wrap}.evidence .badge{margin-right:8px}[hidden]{display:none!important}footer{padding:10px 0 30px}
@media(max-width:700px){main{padding:24px 12px}.panel{padding:16px}.stats{gap:8px}.stats>div{padding:12px}.stats strong{font-size:22px}.results-grid{grid-template-columns:1fr}}
</style></head><body>'''

SCRIPT = '''<script>
const model=document.getElementById('model-filter'), strategy=document.getElementById('strategy-filter'), search=document.getElementById('search'), failures=document.getElementById('failures');
function matches(el){return (!model.value||el.dataset.model===model.value)&&(!strategy.value||el.dataset.strategy===strategy.value)}
function update(){
 document.querySelectorAll('.matrix [data-model]').forEach(el=>el.hidden=!matches(el));
 document.querySelectorAll('.question-row').forEach(row=>{
   const cells=[...row.querySelectorAll('[data-outcome]')].filter(matches);
   row.hidden=!row.dataset.search.toLowerCase().includes(search.value.toLowerCase())||(failures.checked&&!cells.some(c=>['fail','error'].includes(c.dataset.outcome)));
 });
 document.querySelectorAll('.evidence').forEach(el=>el.hidden=!matches(el)||!el.dataset.search.toLowerCase().includes(search.value.toLowerCase())||(failures.checked&&!['fail','error'].includes(el.dataset.outcome)));
}
[model,strategy,search,failures].forEach(el=>el.addEventListener('input',update));
document.querySelectorAll('.matrix a').forEach(link=>link.addEventListener('click',()=>{const target=document.getElementById(link.hash.slice(1));if(target)target.open=true;}));
function revealHash(){const target=document.getElementById(location.hash.slice(1));if(target&&target.tagName==='DETAILS')target.open=true;}
window.addEventListener('hashchange',revealHash);revealHash();
</script>'''
