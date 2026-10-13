# Employee Analytics — Submission Draft

This database models 30 fictional employees, their roles, annual salaries, hiring dates, and manager relationships. A Python CLI accepts questions in plain English, asks a configurable model through OpenRouter to generate SQLite SQL, executes the query, and sends the results back to the model for a plain-language answer. We evaluated Gemini 3.1 Flash Lite and Gemma 3 27B.

Code and database: attach this project's files or add your GitHub repository link before posting. Exclude `.env`.

Schema picture: [schema.svg](diagrams/schema.svg).

## Successful Example

Question: Which employees earn more than their manager? Return employee name, manager name, employee salary in dollars, and manager salary in dollars.

Actual zero-shot SQL:

```sql
SELECT e.name, m.name, e.salary / 100.0, m.salary / 100.0 FROM employee e JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary
```

The actual answer identified Casey Patel ($160,000) and River Mitchell ($220,000), whose manager Alex Chen earns $140,000, and Shawn Phillips ($135,000), whose manager Sam Rivera earns $125,000. These match the reference query results.

## Failed Example (Gemma 3 27B, Zero-shot)

Question: Who reports to Alex Chen, directly or indirectly? Return their names, excluding Alex.

Actual SQL:

```sql
SELECT DISTINCT e2.name FROM employee e1 JOIN employee e2 ON e1.id = e2.manager_id WHERE e1.name = 'Alex Chen' AND e2.name != 'Alex Chen';
```

The answer listed Sam Rivera, Casey Patel, Jamie Kim, Riley Park, Emerson Wright, Charlie Baker, and River Mitchell. These are only the seven direct reports. The reference recursive query returns 13 people, including six indirect reports through Sam Rivera. The generated query executes successfully but does not answer the complete question.

## Database Limitation Example

Question: Who received a promotion last year?

SQL: none generated (`null`). Both models explained that the schema has no promotion or historical job-change information. This is an unsupported question rather than a SQL generation error. No incorrect SQL results were observed in the initial Gemini run; the subsequent Gemma run exposed failures.

## Prompting Results

We compared zero-shot prompting with single-domain few-shot prompting using four separate employee question/SQL demonstrations. Both received the same schema, relationships, sample values, and eight held-out questions. Temperature was zero; there were no automatic repairs or retries.

| Strategy | Correct SQL results | Unsupported question recognized | Input tokens | Output tokens | API-reported cost |
|---|---|---|---|---|---|
| Zero-shot | 8/8 | Yes | 5,563 | 1,419 | $0.00351925 |
| Single-domain few-shot | 8/8 | Yes | 7,120 | 1,486 | $0.00400900 |

The comparison cost $0.00752825 total, excluding the initial smoke test. Few-shot used more tokens without an accuracy improvement in this small experiment. Some output ordering and formatting differed. Reviewing the generated answers found them consistent with the returned data, including salary units, ties, manager counts, and the full hierarchy list. This does not establish performance on other databases or more difficult questions.

The [paper](https://arxiv.org/html/2305.11853v3) studies zero-shot, single-domain, and cross-domain settings. Its findings about database relationships, sample values, and in-domain examples motivated our prompts. Cross-domain demonstrations were not implemented; the assignment permits comparing two strategies.

All eight questions, generated SQL, responses, and results for both strategies are in [results/report.md](../results/report.md). Raw observations and token/cost data are in [results/examples.jsonl](../results/examples.jsonl), with a model-pricing snapshot in [results/run.json](../results/run.json).

## Gemma Comparison

We repeated the same experiment with `google/gemma-3-27b-it`, preserving the database, questions, prompts, temperature, and result-checking procedure. Gemini remains the app's default; Gemma was selected using `--model`.

| Model | Zero-shot correct SQL results | Few-shot correct SQL results | Promotion question declined in both modes | API-reported comparison cost |
|---|---|---|---|---|
| Gemini 3.1 Flash Lite | 8/8 | 8/8 | Yes | $0.00752825 |
| Gemma 3 27B | 6/8 | 7/8 | Yes | $0.001895078 |

Gemma zero-shot failed the highest-salary and hierarchy cases. For highest salary, it returned every employee sorted by salary instead of filtering to the maximum. Its answer still identified the correct two highest earners, showing that an apparently correct answer can hide incorrect SQL. Few-shot fixed that query but failed the hierarchy case by declining to generate SQL and incorrectly claiming that recursive traversal was unsupported in a single read-only SQLite query. SQLite supports the reference recursive query, which Gemini generated successfully.

The few-shot examples improved Gemma's result accuracy on this small run, while neither mode solved its hierarchy case. Answer quality also differed: Gemma returned JSON blocks instead of plain prose for the zero-shot salary-comparison answer. Its few-shot promotion explanation incorrectly characterized `start_date` as the start of the current role; the field represents the hiring date. SQL-result scoring does not capture these wording and format issues.

Gemma was cheaper in this run, but the few-shot hierarchy refusal skipped an answer-generation call, so the totals reflect different call counts as well as different pricing and token usage. Full evidence is in [the Gemma report](../results/gemma-3-27b/report.md), [raw observations](../results/gemma-3-27b/examples.jsonl), and [pricing snapshot](../results/gemma-3-27b/run.json).

## Latest Multi-model Comparison

The [HTML results page](../results/comparisons/initial/index.html) contains a fresh comparison of ten questions (nine SQL questions and one unsupported question), including the added no-boss case. All 60 observations completed without API or execution errors.

| Model | Zero-shot correct SQL | Few-shot correct SQL | API-reported cost |
|---|---|---|---|
| Gemini 3.1 Flash Lite | 9/9 | 9/9 | $0.00798400 |
| Gemma 3 27B | 8/9 | 8/9 | $0.00208919 |
| DeepSeek V3.2 | 9/9 | 9/9 | $0.00679461 |

All three models declined the promotion-history question in both strategies. The comparison cost $0.01686780 total. Gemma missed the hierarchy question in both strategies. Unlike its earlier run, its zero-shot highest-salary query was correct this time; these single-run scores can vary.

The standalone HTML page offers model/strategy filters, question search, a failures-only view, and expandable generated SQL, answers, returned rows, and expected rows. Raw data and selected-case snapshots are preserved in [comparison.json](../results/comparisons/initial/comparison.json) and per-model subdirectories. Future comparisons use the editable list in `employee_analytics/models.py` and questions in `employee_analytics/cases.py`.

## Personal Requirements Still To Complete

- Each person reads the paper, contributes to the database design, and creates their own schema picture.
- Each person runs the app using their individually generated API key and tries a question they personally devised.
- The README specifies an OpenAI-generated key; this project uses the supplied OpenRouter key. Confirm that substitution is accepted or satisfy the OpenAI-key requirement separately.
- Add the repository link or attach code and database, post to the class channel, and self-report in Canvas.
- Read and react or reply to at least three other groups' posts.

