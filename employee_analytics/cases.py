"""Held-out evaluation cases. Money result columns are in dollars."""
CASES = [
    {'id': 'count', 'question': 'How many employees are there?',
     'sql': 'SELECT COUNT(*) FROM employee;'},
    {'id': 'averages', 'question': 'What is the average annual salary in dollars for each role?',
     'sql': 'SELECT role, AVG(salary)/100.0 FROM employee GROUP BY role ORDER BY role;'},
    {'id': 'highest', 'question': 'Who earns the highest annual salary? Include all ties and their salaries in dollars.',
     'sql': 'SELECT name, salary/100.0 FROM employee WHERE salary = (SELECT MAX(salary) FROM employee) ORDER BY name;'},
    {'id': 'dates', 'question': 'Which employees started before January 1, 2023? Return their names and start dates.',
     'sql': "SELECT name, start_date FROM employee WHERE start_date < '2023-01-01' ORDER BY name;"},
    {'id': 'direct', 'question': 'Who reports directly to Alex Chen? Return their names.',
     'sql': "SELECT e.name FROM employee e JOIN employee m ON e.manager_id = m.id WHERE m.name = 'Alex Chen' ORDER BY e.name;"},
    {'id': 'managers', 'question': 'Which managers have at least three direct reports? Return their names and direct report counts, regardless of their role label.',
     'sql': 'SELECT m.name, COUNT(*) FROM employee e JOIN employee m ON e.manager_id = m.id GROUP BY m.id HAVING COUNT(*) >= 3 ORDER BY m.name;'},
    {'id': 'higher_than_manager', 'question': 'Which employees earn more than their manager? Return employee name, manager name, employee salary in dollars, and manager salary in dollars.',
     'sql': 'SELECT e.name, m.name, e.salary/100.0, m.salary/100.0 FROM employee e JOIN employee m ON e.manager_id = m.id WHERE e.salary > m.salary ORDER BY e.name;'},
    {'id': 'hierarchy', 'question': 'Who reports to Alex Chen, directly or indirectly? Return their names, excluding Alex.',
     'sql': "WITH RECURSIVE reports(id,name) AS (SELECT e.id,e.name FROM employee e JOIN employee m ON e.manager_id=m.id WHERE m.name='Alex Chen' UNION ALL SELECT e.id,e.name FROM employee e JOIN reports r ON e.manager_id=r.id) SELECT name FROM reports ORDER BY name;"},
    {'id': 'unsupported', 'question': 'Who received a promotion last year?', 'sql': None},
    {'id': 'noboss', 'question': 'Who doesnt have a boss?',
     'sql': 'SELECT name FROM employee WHERE manager_id IS NULL ORDER BY name;'},
]

