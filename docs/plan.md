# Implementation Plan

Codex will implement a Python CLI that answers natural-language questions about employees using SQLite and an AI model. The user will complete the assignment's personal participation requirements.

## 1. Database

- Use the employee diagram: `id`, `role`, `salary`, `manager_id`, `start_date`; add `name`.
- Make `manager_id` a nullable foreign key to `Employee.id`.
- Define salary as annual USD; store integer cents. Use checked text for roles and `YYYY-MM-DD` dates.
- Seed 25–40 fictional employees with multiple management levels, varied dates, tied salaries, and someone earning more than their manager.
- Update the schema picture to match.

## 2. App

Implement: question → model-generated SQL → SQLite results → model-generated plain-language answer.

- Include schema, relationships, and representative values in the SQL prompt.
- Execute queries through a read-only connection and handle errors.
- Display SQL and the answer; base answers on returned data.
- Keep API keys in environment variables and out of submitted files.

## 3. Prompting Experiment

Compare zero-shot prompting against single-domain few-shot prompting with 3–4 separate question/SQL demonstrations. Keep the model, database, and test questions the same; do not include test questions in demonstrations.

Test these eight questions:

1. How many employees are there?
2. What is the average salary for each role?
3. Who earns the highest salary, including ties?
4. Who started before January 1, 2023?
5. Who reports directly to a selected manager?
6. Which managers have at least three direct reports?
7. Which employees earn more than their manager?
8. Who reports to a selected manager, directly or indirectly?

Write reference SQL first. Record strategy, question, generated SQL, results, answer, correctness, and token usage. Also try an unsupported question about promotion history and record how the app handles it.

Paper: [How to Prompt LLMs for Text-to-SQL](https://arxiv.org/abs/2305.11853). Read all three settings; implementing two is allowed by the README. Cross-domain prompting is optional.

## 4. Implementation and Verification

Codex will complete these steps in order:

1. Create schema and seed scripts, a reproducible SQLite database, and a matching schema diagram.
2. Write reference queries and verify the seeded data covers all eight test cases.
3. Implement API integration, the CLI, both prompting modes, read-only SQL execution, and error handling.
4. Add an experiment runner that compares query results with reference results and saves SQL, answers, correctness, token usage, and estimated API cost.
5. Run local checks for database correctness, query execution, and rejection of database writes.
6. Run live API experiments when the user's API key is available in the environment. If unavailable, finish local verification and document the exact command needed to run the experiments. Never invent API results.
7. Write setup instructions, dependency files, an environment-variable example, and submission notes with actual observed results when available.

Use a configurable model and verify current API usage and pricing during implementation. Keep the scope to a CLI, SQLite, and two prompting modes; cross-domain prompting remains optional.

## 5. Deliverables and User Responsibilities

Codex will prepare:

- Working code, SQLite database, and setup instructions; no API keys.
- Database purpose and schema picture.
- Successful example and failed example, if observed, each with question, SQL, and response.
- File with at least six additional examples.
- Discussion of prompting strategies and observed differences.
- A schema-diagram source that each person can use to create their own picture.

Each person must personally read the paper, create a schema picture, contribute to design, run with their own API key, try their own question, and self-report in Canvas. The user will provide their API key locally, review and submit the project, and read and react or reply to at least three other groups’ posts.

Implementation is complete when the app and experiment runner work, local checks pass, and submission artifacts are ready. Any remaining live API validation must be explicitly documented.

## Implementation Status

Completed: database and seed scripts, schema picture, CLI, configurable OpenRouter integration using Gemini 3.1 Flash Lite, two prompting modes, experiment runner, setup documentation, and submission draft. Five local tests pass. Live experiments produced correct SQL results for all eight questions in both modes, and both declined the unsupported question. The comparison's API-reported cost was $0.00752825. See [setup](SETUP.md), [submission draft](SUBMISSION.md), and [experiment results](../results/report.md).

Files are organized into `employee_analytics/` (application), `data/` (database assets), `tests/`, `docs/` (including `diagrams/`), and `results/`. Run the CLI from the project root with `python3 -m employee_analytics.app`.

Remaining work belongs to the user's personal participation and submission requirements above. OpenRouter replaces the originally planned direct OpenAI integration at the user's request.

A second comparison with Gemma 3 27B scored 6/8 zero-shot and 7/8 few-shot, while both modes declined the unsupported question. API-reported cost was $0.001895078. Evidence is in [the Gemma report](../results/gemma-3-27b/report.md); the submission draft now includes actual Gemma failures and the model comparison.

Completed multi-model refactor: editable `employee_analytics/models.py`, shared experiment runner, and `python3 -m employee_analytics.compare` producing a standalone HTML comparison. Ten local tests pass. The [fresh three-model comparison](../results/comparisons/initial/index.html) completed 60 observations over ten questions and cost $0.01686780. Gemini and DeepSeek scored 9/9 SQL cases in both modes; Gemma scored 8/9 in both. Both original model runs remain preserved.
