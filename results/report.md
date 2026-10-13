# Live Prompting Experiment

Run time (UTC): 2026-10-12T19:23:41.927455+00:00

Requested model: `google/gemini-3.1-flash-lite`. Temperature: 0. Seed database: 30 fictional employees.

Zero-shot and few-shot use the same schema, value samples, model, and held-out questions. Few-shot adds four employee question/SQL examples. No automatic SQL retries or repairs are used.

Correctness compares query result multisets with reference SQL, ignoring row order and aliases. Column order matters, numbers allow small rounding differences. Natural-language answers require manual review; these are observed results on one small database, not a general model benchmark.

| Strategy | Correct SQL / 8 | Unsupported recognized / 1 | Completed / 9 | Errors |
|---|---|---|---|---|
| zero-shot | 8 | 1 | 9 | 0 |
| few-shot | 8 | 1 | 9 | 0 |

Input tokens: 12683. Output tokens: 2905.

Estimated cost using catalog rates: $0.007528.

API-reported cost: $0.007528.

Pricing snapshot: `{"prompt": "0.00000025", "completion": "0.0000015", "image": "0.00000025", "audio": "0.0000005", "input_audio_cache": "0.00000005", "web_search": "0.014", "internal_reasoning": "0.0000015", "input_cache_read": "0.000000025", "input_cache_write": "0.0000000833333333333333"}` (USD per token; estimates do not account for caching or provider differences).

No incorrect SQL results were observed among completed cases. Cases with no reference SQL are scored separately as unsupported questions.

## zero-shot / count

How many employees are there?

Correct: True; status: answered

```sql
SELECT count(*) FROM employee
```

Answer: There are 30 employees.

Returned data:

```json
{
  "columns": [
    "count(*)"
  ],
  "rows": [
    [
      30
    ]
  ],
  "truncated": false
}
```

## zero-shot / averages

What is the average annual salary in dollars for each role?

Correct: True; status: answered

```sql
SELECT role, AVG(salary) / 100.0 FROM employee GROUP BY role
```

Answer: The average annual salaries by role are:

*   **Analyst:** $92,166.67
*   **Designer:** $97,000.00
*   **Engineer:** $132,500.00
*   **Executive:** $220,000.00
*   **Intern:** $47,000.00
*   **Manager:** $135,000.00

Returned data:

```json
{
  "columns": [
    "role",
    "AVG(salary) / 100.0"
  ],
  "rows": [
    [
      "analyst",
      92166.66666666666
    ],
    [
      "designer",
      97000.0
    ],
    [
      "engineer",
      132500.0
    ],
    [
      "executive",
      220000.0
    ],
    [
      "intern",
      47000.0
    ],
    [
      "manager",
      135000.0
    ]
  ],
  "truncated": false
}
```

## zero-shot / highest

Who earns the highest annual salary? Include all ties and their salaries in dollars.

Correct: True; status: answered

```sql
SELECT name, salary / 100.0 FROM employee WHERE salary = (SELECT MAX(salary) FROM employee)
```

Answer: Morgan Lee and River Mitchell earn the highest annual salary of $220,000.00.

Returned data:

```json
{
  "columns": [
    "name",
    "salary / 100.0"
  ],
  "rows": [
    [
      "Morgan Lee",
      220000.0
    ],
    [
      "River Mitchell",
      220000.0
    ]
  ],
  "truncated": false
}
```

## zero-shot / dates

Which employees started before January 1, 2023? Return their names and start dates.

Correct: True; status: answered

```sql
SELECT name, start_date FROM employee WHERE start_date < '2023-01-01'
```

Answer: The following employees started before January 1, 2023:

*   **Morgan Lee:** 2015-02-01
*   **Alex Chen:** 2018-04-15
*   **Jordan Smith:** 2019-07-01
*   **Taylor Brooks:** 2020-01-20
*   **Sam Rivera:** 2021-03-01
*   **Casey Patel:** 2019-08-12
*   **Jamie Kim:** 2022-06-01
*   **Avery Jones:** 2022-11-15
*   **Skyler Wilson:** 2020-10-01
*   **Blake Moore:** 2021-12-01
*   **Dakota Hall:** 2022-01-01
*   **Emerson Wright:** 2021-09-01
*   **Harper Scott:** 2022-05-01
*   **Elliot Nelson:** 2020-03-01
*   **River Mitchell:** 2017-06-01
*   **Robin Perez:** 2022-12-31
*   **Shawn Phillips:** 2021-05-01

Returned data:

```json
{
  "columns": [
    "name",
    "start_date"
  ],
  "rows": [
    [
      "Morgan Lee",
      "2015-02-01"
    ],
    [
      "Alex Chen",
      "2018-04-15"
    ],
    [
      "Jordan Smith",
      "2019-07-01"
    ],
    [
      "Taylor Brooks",
      "2020-01-20"
    ],
    [
      "Sam Rivera",
      "2021-03-01"
    ],
    [
      "Casey Patel",
      "2019-08-12"
    ],
    [
      "Jamie Kim",
      "2022-06-01"
    ],
    [
      "Avery Jones",
      "2022-11-15"
    ],
    [
      "Skyler Wilson",
      "2020-10-01"
    ],
    [
      "Blake Moore",
      "2021-12-01"
    ],
    [
      "Dakota Hall",
      "2022-01-01"
    ],
    [
      "Emerson Wright",
      "2021-09-01"
    ],
    [
      "Harper Scott",
      "2022-05-01"
    ],
    [
      "Elliot Nelson",
      "2020-03-01"
    ],
    [
      "River Mitchell",
      "2017-06-01"
    ],
    [
      "Robin Perez",
      "2022-12-31"
    ],
    [
      "Shawn Phillips",
      "2021-05-01"
    ]
  ],
  "truncated": false
}
```

## zero-shot / direct

Who reports directly to Alex Chen? Return their names.

Correct: True; status: answered

```sql
SELECT e.name FROM employee e JOIN employee m ON e.manager_id = m.id WHERE m.name = 'Alex Chen'
```

Answer: The employees who report directly to Alex Chen are Sam Rivera, Casey Patel, Jamie Kim, Riley Park, Emerson Wright, Charlie Baker, and River Mitchell.

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Sam Rivera"
    ],
    [
      "Casey Patel"
    ],
    [
      "Jamie Kim"
    ],
    [
      "Riley Park"
    ],
    [
      "Emerson Wright"
    ],
    [
      "Charlie Baker"
    ],
    [
      "River Mitchell"
    ]
  ],
  "truncated": false
}
```

## zero-shot / managers

Which managers have at least three direct reports? Return their names and direct report counts, regardless of their role label.

Correct: True; status: answered

```sql
SELECT m.name, COUNT(e.id) AS report_count FROM employee e JOIN employee m ON e.manager_id = m.id GROUP BY m.id HAVING report_count >= 3
```

Answer: The following managers have at least three direct reports:

* **Morgan Lee**: 3
* **Alex Chen**: 7
* **Jordan Smith**: 7
* **Taylor Brooks**: 6
* **Sam Rivera**: 6

Returned data:

```json
{
  "columns": [
    "name",
    "report_count"
  ],
  "rows": [
    [
      "Morgan Lee",
      3
    ],
    [
      "Alex Chen",
      7
    ],
    [
      "Jordan Smith",
      7
    ],
    [
      "Taylor Brooks",
      6
    ],
    [
      "Sam Rivera",
      6
    ]
  ],
  "truncated": false
}
```

## zero-shot / higher_than_manager

Which employees earn more than their manager? Return employee name, manager name, employee salary in dollars, and manager salary in dollars.

Correct: True; status: answered

```sql
SELECT e.name, m.name, e.salary / 100.0, m.salary / 100.0 FROM employee e JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary
```

Answer: The following employees earn more than their managers:

*   **Casey Patel** earns $160,000, while manager **Alex Chen** earns $140,000.
*   **River Mitchell** earns $220,000, while manager **Alex Chen** earns $140,000.
*   **Shawn Phillips** earns $135,000, while manager **Sam Rivera** earns $125,000.

Returned data:

```json
{
  "columns": [
    "name",
    "name",
    "e.salary / 100.0",
    "m.salary / 100.0"
  ],
  "rows": [
    [
      "Casey Patel",
      "Alex Chen",
      160000.0,
      140000.0
    ],
    [
      "River Mitchell",
      "Alex Chen",
      220000.0,
      140000.0
    ],
    [
      "Shawn Phillips",
      "Sam Rivera",
      135000.0,
      125000.0
    ]
  ],
  "truncated": false
}
```

## zero-shot / hierarchy

Who reports to Alex Chen, directly or indirectly? Return their names, excluding Alex.

Correct: True; status: answered

```sql
WITH RECURSIVE subordinates(id, name) AS (SELECT e.id, e.name FROM employee e JOIN employee m ON e.manager_id = m.id WHERE m.name = 'Alex Chen' UNION ALL SELECT e.id, e.name FROM employee e JOIN subordinates s ON e.manager_id = s.id) SELECT name FROM subordinates
```

Answer: The individuals who report to Alex Chen, directly or indirectly, are:

* Sam Rivera
* Casey Patel
* Jamie Kim
* Riley Park
* Emerson Wright
* Charlie Baker
* River Mitchell
* Avery Jones
* Drew Miller
* Quinn Davis
* Logan Green
* Elliot Nelson
* Shawn Phillips

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Sam Rivera"
    ],
    [
      "Casey Patel"
    ],
    [
      "Jamie Kim"
    ],
    [
      "Riley Park"
    ],
    [
      "Emerson Wright"
    ],
    [
      "Charlie Baker"
    ],
    [
      "River Mitchell"
    ],
    [
      "Avery Jones"
    ],
    [
      "Drew Miller"
    ],
    [
      "Quinn Davis"
    ],
    [
      "Logan Green"
    ],
    [
      "Elliot Nelson"
    ],
    [
      "Shawn Phillips"
    ]
  ],
  "truncated": false
}
```

## zero-shot / unsupported

Who received a promotion last year?

Correct: True; status: unsupported

```sql
-- No SQL generated
```

Answer: The database schema does not contain information about promotions or historical job changes; it only stores the current role and start date.

Returned data:

```json
null
```

## few-shot / count

How many employees are there?

Correct: True; status: answered

```sql
SELECT COUNT(*) FROM employee;
```

Answer: There are 30 employees.

Returned data:

```json
{
  "columns": [
    "COUNT(*)"
  ],
  "rows": [
    [
      30
    ]
  ],
  "truncated": false
}
```

## few-shot / averages

What is the average annual salary in dollars for each role?

Correct: True; status: answered

```sql
SELECT role, AVG(salary) / 100.0 AS average_annual_salary_usd FROM employee GROUP BY role
```

Answer: The average annual salaries by role are:

*   **Analyst:** $92,166.67
*   **Designer:** $97,000.00
*   **Engineer:** $132,500.00
*   **Executive:** $220,000.00
*   **Intern:** $47,000.00
*   **Manager:** $135,000.00

Returned data:

```json
{
  "columns": [
    "role",
    "average_annual_salary_usd"
  ],
  "rows": [
    [
      "analyst",
      92166.66666666666
    ],
    [
      "designer",
      97000.0
    ],
    [
      "engineer",
      132500.0
    ],
    [
      "executive",
      220000.0
    ],
    [
      "intern",
      47000.0
    ],
    [
      "manager",
      135000.0
    ]
  ],
  "truncated": false
}
```

## few-shot / highest

Who earns the highest annual salary? Include all ties and their salaries in dollars.

Correct: True; status: answered

```sql
SELECT name, salary / 100.0 AS salary_usd FROM employee WHERE salary = (SELECT MAX(salary) FROM employee)
```

Answer: Morgan Lee and River Mitchell earn the highest annual salary of $220,000.00.

Returned data:

```json
{
  "columns": [
    "name",
    "salary_usd"
  ],
  "rows": [
    [
      "Morgan Lee",
      220000.0
    ],
    [
      "River Mitchell",
      220000.0
    ]
  ],
  "truncated": false
}
```

## few-shot / dates

Which employees started before January 1, 2023? Return their names and start dates.

Correct: True; status: answered

```sql
SELECT name, start_date FROM employee WHERE start_date < '2023-01-01' ORDER BY start_date, name;
```

Answer: The following employees started before January 1, 2023:

*   **Morgan Lee**: 2015-02-01
*   **River Mitchell**: 2017-06-01
*   **Alex Chen**: 2018-04-15
*   **Jordan Smith**: 2019-07-01
*   **Casey Patel**: 2019-08-12
*   **Taylor Brooks**: 2020-01-20
*   **Elliot Nelson**: 2020-03-01
*   **Skyler Wilson**: 2020-10-01
*   **Sam Rivera**: 2021-03-01
*   **Shawn Phillips**: 2021-05-01
*   **Emerson Wright**: 2021-09-01
*   **Blake Moore**: 2021-12-01
*   **Dakota Hall**: 2022-01-01
*   **Harper Scott**: 2022-05-01
*   **Jamie Kim**: 2022-06-01
*   **Avery Jones**: 2022-11-15
*   **Robin Perez**: 2022-12-31

Returned data:

```json
{
  "columns": [
    "name",
    "start_date"
  ],
  "rows": [
    [
      "Morgan Lee",
      "2015-02-01"
    ],
    [
      "River Mitchell",
      "2017-06-01"
    ],
    [
      "Alex Chen",
      "2018-04-15"
    ],
    [
      "Jordan Smith",
      "2019-07-01"
    ],
    [
      "Casey Patel",
      "2019-08-12"
    ],
    [
      "Taylor Brooks",
      "2020-01-20"
    ],
    [
      "Elliot Nelson",
      "2020-03-01"
    ],
    [
      "Skyler Wilson",
      "2020-10-01"
    ],
    [
      "Sam Rivera",
      "2021-03-01"
    ],
    [
      "Shawn Phillips",
      "2021-05-01"
    ],
    [
      "Emerson Wright",
      "2021-09-01"
    ],
    [
      "Blake Moore",
      "2021-12-01"
    ],
    [
      "Dakota Hall",
      "2022-01-01"
    ],
    [
      "Harper Scott",
      "2022-05-01"
    ],
    [
      "Jamie Kim",
      "2022-06-01"
    ],
    [
      "Avery Jones",
      "2022-11-15"
    ],
    [
      "Robin Perez",
      "2022-12-31"
    ]
  ],
  "truncated": false
}
```

## few-shot / direct

Who reports directly to Alex Chen? Return their names.

Correct: True; status: answered

```sql
SELECT e.name FROM employee e JOIN employee m ON e.manager_id = m.id WHERE m.name = 'Alex Chen'
```

Answer: The employees who report directly to Alex Chen are Sam Rivera, Casey Patel, Jamie Kim, Riley Park, Emerson Wright, Charlie Baker, and River Mitchell.

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Sam Rivera"
    ],
    [
      "Casey Patel"
    ],
    [
      "Jamie Kim"
    ],
    [
      "Riley Park"
    ],
    [
      "Emerson Wright"
    ],
    [
      "Charlie Baker"
    ],
    [
      "River Mitchell"
    ]
  ],
  "truncated": false
}
```

## few-shot / managers

Which managers have at least three direct reports? Return their names and direct report counts, regardless of their role label.

Correct: True; status: answered

```sql
SELECT m.name, COUNT(e.id) AS report_count FROM employee e JOIN employee m ON e.manager_id = m.id GROUP BY m.id HAVING report_count >= 3
```

Answer: The following managers have at least three direct reports:

* **Morgan Lee**: 3
* **Alex Chen**: 7
* **Jordan Smith**: 7
* **Taylor Brooks**: 6
* **Sam Rivera**: 6

Returned data:

```json
{
  "columns": [
    "name",
    "report_count"
  ],
  "rows": [
    [
      "Morgan Lee",
      3
    ],
    [
      "Alex Chen",
      7
    ],
    [
      "Jordan Smith",
      7
    ],
    [
      "Taylor Brooks",
      6
    ],
    [
      "Sam Rivera",
      6
    ]
  ],
  "truncated": false
}
```

## few-shot / higher_than_manager

Which employees earn more than their manager? Return employee name, manager name, employee salary in dollars, and manager salary in dollars.

Correct: True; status: answered

```sql
SELECT e.name AS employee_name, m.name AS manager_name, e.salary / 100.0 AS employee_salary_usd, m.salary / 100.0 AS manager_salary_usd FROM employee e JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary
```

Answer: The following employees earn more than their managers:

| Employee Name | Manager Name | Employee Salary (USD) | Manager Salary (USD) |
| :--- | :--- | :--- | :--- |
| Casey Patel | Alex Chen | 160,000.0 | 140,000.0 |
| River Mitchell | Alex Chen | 220,000.0 | 140,000.0 |
| Shawn Phillips | Sam Rivera | 135,000.0 | 125,000.0 |

Returned data:

```json
{
  "columns": [
    "employee_name",
    "manager_name",
    "employee_salary_usd",
    "manager_salary_usd"
  ],
  "rows": [
    [
      "Casey Patel",
      "Alex Chen",
      160000.0,
      140000.0
    ],
    [
      "River Mitchell",
      "Alex Chen",
      220000.0,
      140000.0
    ],
    [
      "Shawn Phillips",
      "Sam Rivera",
      135000.0,
      125000.0
    ]
  ],
  "truncated": false
}
```

## few-shot / hierarchy

Who reports to Alex Chen, directly or indirectly? Return their names, excluding Alex.

Correct: True; status: answered

```sql
WITH RECURSIVE subordinates(id, name) AS (SELECT id, name FROM employee WHERE manager_id = (SELECT id FROM employee WHERE name = 'Alex Chen') UNION ALL SELECT e.id, e.name FROM employee e JOIN subordinates s ON e.manager_id = s.id) SELECT name FROM subordinates ORDER BY name;
```

Answer: The individuals who report to Alex Chen, directly or indirectly, are:

*   Avery Jones
*   Casey Patel
*   Charlie Baker
*   Drew Miller
*   Elliot Nelson
*   Emerson Wright
*   Jamie Kim
*   Logan Green
*   Quinn Davis
*   Riley Park
*   River Mitchell
*   Sam Rivera
*   Shawn Phillips

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Avery Jones"
    ],
    [
      "Casey Patel"
    ],
    [
      "Charlie Baker"
    ],
    [
      "Drew Miller"
    ],
    [
      "Elliot Nelson"
    ],
    [
      "Emerson Wright"
    ],
    [
      "Jamie Kim"
    ],
    [
      "Logan Green"
    ],
    [
      "Quinn Davis"
    ],
    [
      "Riley Park"
    ],
    [
      "River Mitchell"
    ],
    [
      "Sam Rivera"
    ],
    [
      "Shawn Phillips"
    ]
  ],
  "truncated": false
}
```

## few-shot / unsupported

Who received a promotion last year?

Correct: True; status: unsupported

```sql
-- No SQL generated
```

Answer: The database schema does not contain information about promotions or historical job titles, making it impossible to determine if an employee received a promotion.

Returned data:

```json
null
```
