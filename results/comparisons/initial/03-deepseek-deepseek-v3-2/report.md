# Live Prompting Experiment

Run time (UTC): 2026-10-13T00:44:54.264599+00:00

Requested model: `deepseek/deepseek-v3.2`. Temperature: 0. Seed database: 30 fictional employees.

Zero-shot and few-shot use the same schema, value samples, model, and held-out questions. Few-shot adds four employee question/SQL examples. No automatic SQL retries or repairs are used.

Correctness compares query result multisets with reference SQL, ignoring row order and aliases. Column order matters, numbers allow small rounding differences. Natural-language answers require manual review; these are observed results on one small database, not a general model benchmark.

| Strategy | Correct SQL / 9 | Unsupported recognized / 1 | Completed / 10 | Errors |
|---|---|---|---|---|
| zero-shot | 9 | 1 | 10 | 0 |
| few-shot | 9 | 1 | 10 | 0 |

Input tokens: 12664. Output tokens: 3312.

Estimated cost using catalog rates: $0.005930.

API-reported cost: $0.006795.

Pricing snapshot: `{"prompt": "0.000000259", "completion": "0.0000008", "input_cache_read": "0.00000014"}` (USD per token; estimates do not account for caching or provider differences).

No incorrect SQL results were observed among completed cases. Cases with no reference SQL are scored separately as unsupported questions.

## zero-shot / count

How many employees are there?

Correct: True; status: answered

```sql
SELECT COUNT(*) AS count FROM employee;
```

Answer: There are 30 employees.

Returned data:

```json
{
  "columns": [
    "count"
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
SELECT role, AVG(salary) / 100.0 AS average_salary_dollars FROM employee GROUP BY role ORDER BY role;
```

Answer: Based on the query results, the average annual salary in dollars for each role is as follows:

*   Analyst: $92,166.67
*   Designer: $97,000.00
*   Engineer: $132,500.00
*   Executive: $220,000.00
*   Intern: $47,000.00
*   Manager: $135,000.00

The results are complete and not truncated.

Returned data:

```json
{
  "columns": [
    "role",
    "average_salary_dollars"
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
SELECT name, salary / 100.0 AS salary_dollars FROM employee WHERE salary = (SELECT MAX(salary) FROM employee);
```

Answer: Morgan Lee and River Mitchell each earn the highest annual salary, which is $220,000.

Returned data:

```json
{
  "columns": [
    "name",
    "salary_dollars"
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
SELECT name, start_date FROM employee WHERE start_date < '2023-01-01' ORDER BY start_date;
```

Answer: The employees who started before January 1, 2023, along with their start dates, are:

- Morgan Lee (2015-02-01)
- River Mitchell (2017-06-01)
- Alex Chen (2018-04-15)
- Jordan Smith (2019-07-01)
- Casey Patel (2019-08-12)
- Taylor Brooks (2020-01-20)
- Elliot Nelson (2020-03-01)
- Skyler Wilson (2020-10-01)
- Sam Rivera (2021-03-01)
- Shawn Phillips (2021-05-01)
- Emerson Wright (2021-09-01)
- Blake Moore (2021-12-01)
- Dakota Hall (2022-01-01)
- Harper Scott (2022-05-01)
- Jamie Kim (2022-06-01)
- Avery Jones (2022-11-15)
- Robin Perez (2022-12-31)

The results are complete (not truncated).

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

## zero-shot / direct

Who reports directly to Alex Chen? Return their names.

Correct: True; status: answered

```sql
SELECT e2.name FROM employee e1 JOIN employee e2 ON e1.id = e2.manager_id WHERE e1.name = 'Alex Chen';
```

Answer: Alex Chen has seven direct reports: Sam Rivera, Casey Patel, Jamie Kim, Riley Park, Emerson Wright, Charlie Baker, and River Mitchell.

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
SELECT e.name AS manager_name, COUNT(r.id) AS direct_report_count FROM employee e LEFT JOIN employee r ON e.id = r.manager_id GROUP BY e.id HAVING COUNT(r.id) >= 3 ORDER BY direct_report_count DESC;
```

Answer: The managers with at least three direct reports are:

- Alex Chen (7 direct reports)
- Jordan Smith (7 direct reports)
- Taylor Brooks (6 direct reports)
- Sam Rivera (6 direct reports)
- Morgan Lee (3 direct reports)

Returned data:

```json
{
  "columns": [
    "manager_name",
    "direct_report_count"
  ],
  "rows": [
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
    ],
    [
      "Morgan Lee",
      3
    ]
  ],
  "truncated": false
}
```

## zero-shot / higher_than_manager

Which employees earn more than their manager? Return employee name, manager name, employee salary in dollars, and manager salary in dollars.

Correct: True; status: answered

```sql
SELECT e.name AS employee_name, m.name AS manager_name, e.salary / 100.0 AS employee_salary_dollars, m.salary / 100.0 AS manager_salary_dollars FROM employee e INNER JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary;
```

Answer: Based on the query results, the following employees earn more than their managers:

- **Casey Patel** earns $160,000, while their manager **Alex Chen** earns $140,000.
- **River Mitchell** earns $220,000, while their manager **Alex Chen** earns $140,000.
- **Shawn Phillips** earns $135,000, while their manager **Sam Rivera** earns $125,000.

Returned data:

```json
{
  "columns": [
    "employee_name",
    "manager_name",
    "employee_salary_dollars",
    "manager_salary_dollars"
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
WITH RECURSIVE reports AS (SELECT id, name, manager_id FROM employee WHERE manager_id = (SELECT id FROM employee WHERE name = 'Alex Chen') UNION ALL SELECT e.id, e.name, e.manager_id FROM employee e INNER JOIN reports r ON e.manager_id = r.id) SELECT name FROM reports;
```

Answer: The following employees report to Alex Chen, either directly or indirectly:

- Sam Rivera
- Casey Patel
- Jamie Kim
- Riley Park
- Emerson Wright
- Charlie Baker
- River Mitchell
- Avery Jones
- Drew Miller
- Quinn Davis
- Logan Green
- Elliot Nelson
- Shawn Phillips

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

Answer: The question asks about promotions, but the schema does not include any column or data that tracks promotions or role changes over time. The 'role' column is static per employee record, and there is no historical data on role transitions. Therefore, it is impossible to determine from this database who received a promotion last year.

Returned data:

```json
null
```

## zero-shot / noboss

Who doesnt have a boss?

Correct: True; status: answered

```sql
SELECT name FROM employee WHERE manager_id IS NULL;
```

Answer: Morgan Lee does not have a boss.

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Morgan Lee"
    ]
  ],
  "truncated": false
}
```

## few-shot / count

How many employees are there?

Correct: True; status: answered

```sql
SELECT COUNT(*) AS employee_count FROM employee;
```

Answer: There are 30 employees.

Returned data:

```json
{
  "columns": [
    "employee_count"
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
SELECT role, AVG(salary) / 100.0 AS average_annual_salary_usd FROM employee GROUP BY role ORDER BY role;
```

Answer: Based on the query results, the average annual salary in USD for each role is as follows:

*   Analyst: $92,166.67
*   Designer: $97,000.00
*   Engineer: $132,500.00
*   Executive: $220,000.00
*   Intern: $47,000.00
*   Manager: $135,000.00

The results are complete and not truncated.

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
SELECT name, salary / 100.0 AS annual_salary_usd FROM employee WHERE salary = (SELECT MAX(salary) FROM employee) ORDER BY name;
```

Answer: Morgan Lee and River Mitchell earn the highest annual salary, each with an annual salary of $220,000.

Returned data:

```json
{
  "columns": [
    "name",
    "annual_salary_usd"
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
SELECT name, start_date FROM employee WHERE start_date < '2023-01-01' ORDER BY name;
```

Answer: The employees who started before January 1, 2023, are as follows:

| Name            | Start Date   |
|-----------------|--------------|
| Alex Chen       | 2018-04-15   |
| Avery Jones     | 2022-11-15   |
| Blake Moore     | 2021-12-01   |
| Casey Patel     | 2019-08-12   |
| Dakota Hall     | 2022-01-01   |
| Elliot Nelson   | 2020-03-01   |
| Emerson Wright  | 2021-09-01   |
| Harper Scott    | 2022-05-01   |
| Jamie Kim       | 2022-06-01   |
| Jordan Smith    | 2019-07-01   |
| Morgan Lee      | 2015-02-01   |
| River Mitchell  | 2017-06-01   |
| Robin Perez     | 2022-12-31   |
| Sam Rivera      | 2021-03-01   |
| Shawn Phillips  | 2021-05-01   |
| Skyler Wilson   | 2020-10-01   |
| Taylor Brooks   | 2020-01-20   |

Returned data:

```json
{
  "columns": [
    "name",
    "start_date"
  ],
  "rows": [
    [
      "Alex Chen",
      "2018-04-15"
    ],
    [
      "Avery Jones",
      "2022-11-15"
    ],
    [
      "Blake Moore",
      "2021-12-01"
    ],
    [
      "Casey Patel",
      "2019-08-12"
    ],
    [
      "Dakota Hall",
      "2022-01-01"
    ],
    [
      "Elliot Nelson",
      "2020-03-01"
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
      "Jamie Kim",
      "2022-06-01"
    ],
    [
      "Jordan Smith",
      "2019-07-01"
    ],
    [
      "Morgan Lee",
      "2015-02-01"
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
      "Sam Rivera",
      "2021-03-01"
    ],
    [
      "Shawn Phillips",
      "2021-05-01"
    ],
    [
      "Skyler Wilson",
      "2020-10-01"
    ],
    [
      "Taylor Brooks",
      "2020-01-20"
    ]
  ],
  "truncated": false
}
```

## few-shot / direct

Who reports directly to Alex Chen? Return their names.

Correct: True; status: answered

```sql
SELECT e.name FROM employee e JOIN employee m ON e.manager_id = m.id WHERE m.name = 'Alex Chen' ORDER BY e.name;
```

Answer: Alex Chen has seven direct reports: Casey Patel, Charlie Baker, Emerson Wright, Jamie Kim, Riley Park, River Mitchell, and Sam Rivera.

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Casey Patel"
    ],
    [
      "Charlie Baker"
    ],
    [
      "Emerson Wright"
    ],
    [
      "Jamie Kim"
    ],
    [
      "Riley Park"
    ],
    [
      "River Mitchell"
    ],
    [
      "Sam Rivera"
    ]
  ],
  "truncated": false
}
```

## few-shot / managers

Which managers have at least three direct reports? Return their names and direct report counts, regardless of their role label.

Correct: True; status: answered

```sql
SELECT e.name, COUNT(r.id) AS direct_report_count FROM employee e LEFT JOIN employee r ON e.id = r.manager_id GROUP BY e.id HAVING direct_report_count >= 3 ORDER BY e.name;
```

Answer: According to the query results, the following managers have at least three direct reports:

| Name | Direct Report Count |
|------|---------------------|
| Alex Chen | 7 |
| Jordan Smith | 7 |
| Morgan Lee | 3 |
| Sam Rivera | 6 |
| Taylor Brooks | 6 |

Returned data:

```json
{
  "columns": [
    "name",
    "direct_report_count"
  ],
  "rows": [
    [
      "Alex Chen",
      7
    ],
    [
      "Jordan Smith",
      7
    ],
    [
      "Morgan Lee",
      3
    ],
    [
      "Sam Rivera",
      6
    ],
    [
      "Taylor Brooks",
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
SELECT e.name AS employee_name, m.name AS manager_name, e.salary / 100.0 AS employee_salary_usd, m.salary / 100.0 AS manager_salary_usd FROM employee e JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary ORDER BY e.name;
```

Answer: The employees who earn more than their manager are:

- Casey Patel earns $160,000 while their manager Alex Chen earns $140,000.
- River Mitchell earns $220,000 while their manager Alex Chen earns $140,000.
- Shawn Phillips earns $135,000 while their manager Sam Rivera earns $125,000.

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
WITH RECURSIVE reports AS (SELECT id, name, manager_id FROM employee WHERE name = 'Alex Chen' UNION ALL SELECT e.id, e.name, e.manager_id FROM employee e INNER JOIN reports r ON e.manager_id = r.id) SELECT name FROM reports WHERE name != 'Alex Chen' ORDER BY name;
```

Answer: Based on the query results, the following individuals report to Alex Chen, either directly or indirectly:

- Avery Jones
- Casey Patel
- Charlie Baker
- Drew Miller
- Elliot Nelson
- Emerson Wright
- Jamie Kim
- Logan Green
- Quinn Davis
- Riley Park
- River Mitchell
- Sam Rivera
- Shawn Phillips

The list includes 13 names and is complete (not truncated).

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

Answer: The question asks about promotions, but the schema does not contain promotion history or role change tracking. The start_date represents hiring date, not promotion dates. Therefore, this question cannot be answered from the given database.

Returned data:

```json
null
```

## few-shot / noboss

Who doesnt have a boss?

Correct: True; status: answered

```sql
SELECT name FROM employee WHERE manager_id IS NULL ORDER BY name;
```

Answer: Morgan Lee does not have a boss.

Returned data:

```json
{
  "columns": [
    "name"
  ],
  "rows": [
    [
      "Morgan Lee"
    ]
  ],
  "truncated": false
}
```
