# Live Prompting Experiment

Run time (UTC): 2026-10-12T19:32:18.623994+00:00

Requested model: `google/gemma-3-27b-it`. Temperature: 0. Seed database: 30 fictional employees.

Zero-shot and few-shot use the same schema, value samples, model, and held-out questions. Few-shot adds four employee question/SQL examples. No automatic SQL retries or repairs are used.

Correctness compares query result multisets with reference SQL, ignoring row order and aliases. Column order matters, numbers allow small rounding differences. Natural-language answers require manual review; these are observed results on one small database, not a general model benchmark.

| Strategy | Correct SQL / 8 | Unsupported recognized / 1 | Completed / 9 | Errors |
|---|---|---|---|---|
| zero-shot | 6 | 1 | 9 | 0 |
| few-shot | 7 | 1 | 9 | 0 |

Input tokens: 13252. Output tokens: 2819.

Estimated cost using catalog rates: $0.002329.

API-reported cost: $0.001895.

Pricing snapshot: `{"prompt": "0.00000008", "completion": "0.00000045", "input_cache_read": "0.00000004"}` (USD per token; estimates do not account for caching or provider differences).

## zero-shot / count

How many employees are there?

Correct: True; status: answered

```sql
SELECT count(*) FROM employee
```

Answer: 
There are 30 employees.

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
SELECT role, AVG(salary / 100.0) FROM employee GROUP BY role;
```

Answer: 
The average annual salaries are: analyst ($92,166.67), designer ($97,000.00), engineer ($132,500.00), executive ($220,000.00), intern ($47,000.00), and manager ($135,000.00).

Returned data:

```json
{
  "columns": [
    "role",
    "AVG(salary / 100.0)"
  ],
  "rows": [
    [
      "analyst",
      92166.66666666667
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

Correct: False; status: answered

```sql
SELECT name, salary / 100.0 FROM employee ORDER BY salary DESC
```

Answer: 
Morgan Lee and River Mitchell both earn the highest annual salary of $220000.0.

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
    ],
    [
      "Casey Patel",
      160000.0
    ],
    [
      "Jordan Smith",
      145000.0
    ],
    [
      "Alex Chen",
      140000.0
    ],
    [
      "Shawn Phillips",
      135000.0
    ],
    [
      "Taylor Brooks",
      130000.0
    ],
    [
      "Emerson Wright",
      130000.0
    ],
    [
      "Sam Rivera",
      125000.0
    ],
    [
      "Elliot Nelson",
      125000.0
    ],
    [
      "Dakota Hall",
      120000.0
    ],
    [
      "Avery Jones",
      115000.0
    ],
    [
      "Jamie Kim",
      110000.0
    ],
    [
      "Logan Green",
      110000.0
    ],
    [
      "Reese Clark",
      105000.0
    ],
    [
      "Drew Miller",
      100000.0
    ],
    [
      "Finley Young",
      100000.0
    ],
    [
      "Sage Carter",
      100000.0
    ],
    [
      "Riley Park",
      95000.0
    ],
    [
      "Blake Moore",
      95000.0
    ],
    [
      "Harper Scott",
      95000.0
    ],
    [
      "Robin Perez",
      95000.0
    ],
    [
      "Skyler Wilson",
      90000.0
    ],
    [
      "Cameron Adams",
      90000.0
    ],
    [
      "Marley Turner",
      88000.0
    ],
    [
      "Rowan King",
      85000.0
    ],
    [
      "Charlie Baker",
      50000.0
    ],
    [
      "Jules Roberts",
      48000.0
    ],
    [
      "Quinn Davis",
      45000.0
    ],
    [
      "Peyton Lewis",
      45000.0
    ]
  ],
  "truncated": false
}
```

Expected data:

```json
{
  "columns": [
    "name",
    "salary/100.0"
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

Answer: 
Morgan Lee started on 2015-02-01, Alex Chen on 2018-04-15, Jordan Smith on 2019-07-01, Taylor Brooks on 2020-01-20, Sam Rivera on 2021-03-01, Casey Patel on 2019-08-12, Jamie Kim on 2022-06-01, Avery Jones on 2022-11-15, Skyler Wilson on 2020-10-01, Blake Moore on 2021-12-01, Dakota Hall on 2022-01-01, Emerson Wright on 2021-09-01, Harper Scott on 2022-05-01, Elliot Nelson on 2020-03-01, River Mitchell on 2017-06-01, Robin Perez on 2022-12-31, and Shawn Phillips on 2021-05-01.

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
SELECT e.name FROM employee e WHERE e.manager_id = (SELECT id FROM employee WHERE name = 'Alex Chen');
```

Answer: 
Sam Rivera, Casey Patel, Jamie Kim, Riley Park, Emerson Wright, Charlie Baker, and River Mitchell report directly to Alex Chen.

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
SELECT e1.name, COUNT(e2.id) AS direct_report_count FROM employee AS e1 JOIN employee AS e2 ON e1.id = e2.manager_id GROUP BY e1.id HAVING COUNT(e2.id) >= 3;
```

Answer: 
Morgan Lee, Alex Chen, Jordan Smith, Taylor Brooks, and Sam Rivera have at least three direct reports. Their direct report counts are 3, 7, 7, 6, and 6 respectively.

Returned data:

```json
{
  "columns": [
    "name",
    "direct_report_count"
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
SELECT
  e.name AS employee_name,
  m.name AS manager_name,
  e.salary / 100.0 AS employee_salary,
  m.salary / 100.0 AS manager_salary
FROM employee AS e
JOIN employee AS m
  ON e.manager_id = m.id
WHERE
  e.salary > m.salary;
```

Answer: 
```json
{
  "employee_name": "Casey Patel",
  "manager_name": "Alex Chen",
  "employee_salary": 160000.0,
  "manager_salary": 140000.0
}
```

```json
{
  "employee_name": "River Mitchell",
  "manager_name": "Alex Chen",
  "employee_salary": 220000.0,
  "manager_salary": 140000.0
}
```

```json
{
  "employee_name": "Shawn Phillips",
  "manager_name": "Sam Rivera",
  "employee_salary": 135000.0,
  "manager_salary": 125000.0
}
```

Returned data:

```json
{
  "columns": [
    "employee_name",
    "manager_name",
    "employee_salary",
    "manager_salary"
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

Correct: False; status: answered

```sql
SELECT DISTINCT e2.name FROM employee e1 JOIN employee e2 ON e1.id = e2.manager_id WHERE e1.name = 'Alex Chen' AND e2.name != 'Alex Chen';
```

Answer: 
Sam Rivera, Casey Patel, Jamie Kim, Riley Park, Emerson Wright, Charlie Baker, and River Mitchell report to Alex Chen.

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

Expected data:

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

## zero-shot / unsupported

Who received a promotion last year?

Correct: True; status: unsupported

```sql
-- No SQL generated
```

Answer: The schema does not contain information about promotions. It only stores the start date of employment, which does not necessarily indicate a promotion. Therefore, it is impossible to determine who received a promotion last year based on the provided schema.

Returned data:

```json
null
```

## few-shot / count

How many employees are there?

Correct: True; status: answered

```sql
SELECT COUNT(*) AS employee_count FROM employee;
```

Answer: 
There are 30 employees.

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
SELECT role, AVG(salary) / 100.0 AS average_salary_usd FROM employee GROUP BY role ORDER BY role;
```

Answer: 
The average annual salary for each role is as follows: analyst ($92,166.67), designer ($97,000.00), engineer ($132,500.00), executive ($220,000.00), intern ($47,000.00), and manager ($135,000.00).

Returned data:

```json
{
  "columns": [
    "role",
    "average_salary_usd"
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

Answer: 
Morgan Lee and River Mitchell both earn the highest annual salary of $220000.0.

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

Answer: 
Alex Chen started on 2018-04-15.
Avery Jones started on 2022-11-15.
Blake Moore started on 2021-12-01.
Casey Patel started on 2019-08-12.
Dakota Hall started on 2022-01-01.
Elliot Nelson started on 2020-03-01.
Emerson Wright started on 2021-09-01.
Harper Scott started on 2022-05-01.
Jamie Kim started on 2022-06-01.
Jordan Smith started on 2019-07-01.
Morgan Lee started on 2015-02-01.
River Mitchell started on 2017-06-01.
Robin Perez started on 2022-12-31.
Sam Rivera started on 2021-03-01.
Shawn Phillips started on 2021-05-01.
Skyler Wilson started on 2020-10-01.
Taylor Brooks started on 2020-01-20.

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

Answer: 
Casey Patel, Charlie Baker, Emerson Wright, Jamie Kim, Riley Park, River Mitchell, and Sam Rivera report directly to Alex Chen.

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
SELECT m.name, COUNT(e.id) AS direct_report_count FROM employee e JOIN employee m ON e.manager_id = m.id GROUP BY m.id HAVING COUNT(e.id) >= 3 ORDER BY m.name;
```

Answer: 
Alex Chen has 7 direct reports, Jordan Smith has 7 direct reports, Morgan Lee has 3 direct reports, Sam Rivera has 6 direct reports, and Taylor Brooks has 6 direct reports.

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
SELECT e.name AS employee_name, m.name AS manager_name, e.salary / 100.0 AS employee_salary_usd, m.salary / 100.0 AS manager_salary_usd FROM employee e JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary ORDER BY employee_name, manager_name;
```

Answer: 
Casey Patel earns more than Alex Chen ($160000.0 vs $140000.0). River Mitchell earns more than Alex Chen ($220000.0 vs $140000.0). Shawn Phillips earns more than Sam Rivera ($135000.0 vs $125000.0).





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

Correct: False; status: unsupported

```sql
-- No SQL generated
```

Answer: This query requires recursive traversal to find indirect reports, which is not supported by a single read-only SQLite query. The schema does not provide a way to efficiently determine all levels of subordinates without recursion.

Returned data:

```json
null
```

Expected data:

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

Answer: The question asks about promotions, but the schema does not contain information about promotions. It only contains the start date, which represents the date the employee started their current role, not necessarily a promotion date. Therefore, this question cannot be answered from the provided database schema.

Returned data:

```json
null
```
