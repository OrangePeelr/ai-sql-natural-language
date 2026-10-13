# Employee Analytics

A natural-language interface to 30 fictional employees, their annual salaries, hiring dates, and reporting relationships. Python 3.10+ is required; no third-party dependencies are needed.

## Run

Run commands from the project root. Keep `.env` in the project root using [`.env.example`](../.env.example) as a guide. Set `OPENROUTER_API_KEY`; the existing `OPEN_ROUTER` variable also works. Never commit `.env` or share the key.

```sh
python3 -m employee_analytics.app "Who earns more than their manager?"
python3 -m employee_analytics.app --strategy few-shot
python3 -m unittest discover -s tests -v
python3 -m employee_analytics.experiment --output results/new-run
```

The supplied database is ready to use. The app and experiment runner create `data/employees.db` automatically when missing. You can also initialize a missing database with `python3 -m employee_analytics.database`; initialization refuses to overwrite an existing database. Use `data/schema.sql` and `data/seed.sql` to reproduce it.

The default model is `google/gemini-3.1-flash-lite`. Set `OPENROUTER_MODEL` in `.env` or pass `--model` to either command to change it:

```sh
python3 -m employee_analytics.app --model deepseek/deepseek-v3.2 "How many employees are there?"
python3 -m employee_analytics.experiment --model deepseek/deepseek-v3.2 --output results/deepseek
python3 -m employee_analytics.experiment --model google/gemma-3-27b-it --output results/gemma-new-run
```

Each supported question makes two API calls: one for SQL, one for the answer. Unsupported questions make one. A complete comparison uses up to 36 calls. Calls can incur small charges; `results/run.json` captures live catalog pricing and records contain estimated and API-reported costs. No automatic paid retries occur.

## Results and files

- `data/schema.sql`, `data/seed.sql`, `data/employees.db`: schema, reproducible data, and ready-to-use database.
- `docs/diagrams/schema.svg`: matching schema picture and editable source. Original diagrams are preserved in the same folder.
- `employee_analytics/app.py`, `client.py`, `database.py`, `prompts.py`: package modules for the CLI, OpenRouter calls, restricted execution, and prompts.
- `employee_analytics/cases.py`: eight held-out questions with reference SQL, plus an unsupported question.
- `employee_analytics/experiment.py`: compares results across zero-shot and four-example single-domain few-shot prompts.
- `employee_analytics/models.py`: editable model list for comparisons.
- `employee_analytics/compare.py`, `employee_analytics/html_report.py`: multi-model runner and standalone HTML report generator.
- `results/examples.jsonl`: actual questions, SQL, returned rows, answers, references, correctness, and usage.
- `results/report.md`: readable experiment results for submission.
- `results/gemma-3-27b/`: separate comparison using Gemma 3 27B; the original Gemini evidence remains in `results/`.
- `tests/test_project.py`: database, reference-query, restriction, execution-limit, and pipeline checks.
- `tests/test_comparison.py`: configurable model selections, failure isolation, saved evidence, and safe HTML rendering.

```text
.
├── README.md
├── .env / .env.example
├── requirements.txt
├── employee_analytics/   # Python package
├── data/                 # SQL scripts and SQLite database
├── tests/                # Local verification
├── docs/                 # Setup, plan, submission draft
│   └── diagrams/         # Current and original schema pictures
└── results/              # Saved live experiment evidence
```

Database assets, `.env`, and the default results directory are resolved relative to the project root, independently of the current working directory. Custom `--output` paths are relative to your current working directory unless absolute.

Use a new `--output` directory for each experiment. The runner saves every observation immediately and refuses to overwrite existing results. `--limit 1` runs a two-strategy smoke test.

Add test questions to `CASES` in `employee_analytics/cases.py`, with a unique `id`, a `question`, and reference `sql` (`None` for an unsupported question). The runner selects all cases by default; `--limit N` selects the first N. Report totals automatically count the selected SQL and unsupported cases separately, and show completed cases while the run progresses. Each new `run.json` snapshots the selected cases so its counts remain accurate if you edit `cases.py` later.

## Compare Models in HTML

Edit `MODELS` in [employee_analytics/models.py](../employee_analytics/models.py) to add or remove OpenRouter model IDs. The initial list contains Gemini 3.1 Flash Lite, Gemma 3 27B, and DeepSeek V3.2. Every selected model receives both prompting strategies and the same selected questions from `cases.py`.

```sh
python3 -m employee_analytics.compare
```

This creates a new timestamped directory under `results/comparisons/`. Open its `index.html` directly in your browser; no server or installation is required. The page includes model scores, unsupported-question recognition, completed counts, tokens, API-reported costs, a question matrix, and expandable SQL/answer/expected-result evidence. Filter by model, strategy, question text, or failures. Reload the page to see progress during a live run.

Override the configured list for a particular run, or run a quick comparison:

```sh
python3 -m employee_analytics.compare --models google/gemma-3-27b-it deepseek/deepseek-v3.2 --output results/comparisons/custom
python3 -m employee_analytics.compare --limit 1
```

Each `--output` directory must be new. Models and cases are snapshotted in `comparison.json`; changing either configuration affects future runs. Each model also gets its own `run.json`, `examples.jsonl`, and Markdown report. An API failure stops that model's run but allows the other models to continue; unrun cases are marked pending rather than counted as observed failures. Answer refusals and wrong SQL remain visible as failed cases.

Rebuild an existing comparison page without API calls:

```sh
python3 -m employee_analytics.compare --render-only results/comparisons/initial
```

The initial live HTML comparison is at [results/comparisons/initial/index.html](../results/comparisons/initial/index.html). The older single-model results remain in their original folders.

Every supported question uses two paid calls; an unsupported question uses one. With ten cases and three models, a complete run uses up to 120 calls. No automatic retries occur. Costs in the page cover recorded usage, which may exclude calls that fail before returning usage. Correctness scores compare query results; review plain-language answers separately.

SQL is limited to reads of the employee table with a three-second execution budget and 200-row result cap. Recursive reads are supported; writes, attachments, pragmas, and extension loading are rejected. Truncated results are marked incomplete. Conversations are independent questions, without previous-question context.

Salary is annual USD cents in storage, and dollars in query outputs. Roles use a SQLite text constraint; dates are ISO text. `manager_id` is a nullable self-reference. The database has no promotion or historical salary data. Constraints do not enforce an acyclic management graph; the provided seed hierarchy is acyclic.

The experiment checks SQL results, not answer quality. Review plain-language answers yourself. A single small experiment cannot establish general model accuracy, and one seeded database can hide some semantically incorrect queries.

## Sources

- [Original assignment instructions](assignment.md)
- [Prompting paper](https://arxiv.org/html/2305.11853v3): schema relationships, content representation, and demonstrations motivate the comparison.
- [OpenRouter API documentation](https://openrouter.ai/docs/api_reference/overview): chat completion request format and usage fields.
- [OpenRouter model catalog](https://openrouter.ai/api/v1/models): current model IDs and pricing; fetched by the experiment runner.

The original assignment instructions require each person to generate and run with their own OpenAI API key. This implementation uses the OpenRouter key you supplied; confirm that substitution is accepted for your class or satisfy the OpenAI requirement separately.

