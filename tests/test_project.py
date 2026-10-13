import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from employee_analytics.app import ask
from employee_analytics.cases import CASES
from employee_analytics.database import initialize, query
from employee_analytics.experiment import equivalent, write_report


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'test.db'
        initialize(self.path)

    def test_seed_and_reference_queries(self):
        self.assertEqual(query(CASES[0]['sql'], self.path)['rows'], [[30]])
        self.assertEqual(len(query(CASES[2]['sql'], self.path)['rows']), 2)
        self.assertEqual(len(query(CASES[4]['sql'], self.path)['rows']), 7)
        self.assertEqual(len(query(CASES[7]['sql'], self.path)['rows']), 13)
        self.assertEqual(len(query(CASES[6]['sql'], self.path)['rows']), 3)
        for case in CASES:
            if case['sql']:
                self.assertFalse(query(case['sql'], self.path)['truncated'])

    def test_mutations_and_other_resources_are_rejected(self):
        for sql in ('DELETE FROM employee', 'DROP TABLE employee',
                    'UPDATE employee SET salary=0', "ATTACH DATABASE ':memory:' AS other",
                    'PRAGMA query_only=OFF', 'SELECT * FROM sqlite_master',
                    "SELECT load_extension('anything')", 'SELECT 1; DELETE FROM employee;'):
            with self.subTest(sql=sql), self.assertRaises(sqlite3.Error):
                query(sql, self.path)
        self.assertEqual(query('SELECT COUNT(*) FROM employee', self.path)['rows'], [[30]])

    def test_limits(self):
        result = query('SELECT name FROM employee', self.path, max_rows=2)
        self.assertTrue(result['truncated'])
        self.assertEqual(len(result['rows']), 2)
        with self.assertRaises(sqlite3.OperationalError):
            query('WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n) SELECT SUM(x) FROM n', self.path)

    def test_result_comparison(self):
        a = {'rows': [['a', 2.00000001], ['b', 3]], 'truncated': False}
        b = {'rows': [['b', 3], ['a', 2]], 'truncated': False}
        self.assertTrue(equivalent(a, b))
        self.assertFalse(equivalent(a, {'rows': [['a', 2], ['a', 2]], 'truncated': False}))
        self.assertFalse(equivalent({**a, 'truncated': True}, b))

    def test_pipeline_and_unsupported(self):
        class FakeClient:
            model = 'test-only'
            def __init__(self, responses):
                self.responses = iter(responses)
            def complete(self, messages, json_output=False):
                return next(self.responses), {'model': self.model, 'usage': {}}
        with patch('employee_analytics.app.query', lambda sql: query(sql, self.path)), patch('employee_analytics.prompts.query', lambda sql: query(sql, self.path)):
            client = FakeClient(['{"sql":"SELECT COUNT(*) FROM employee","reason":""}', 'There are 30 employees.'])
            result = ask(client, 'How many employees?', 'few-shot')
            self.assertEqual(result['status'], 'answered')
            self.assertEqual(len(result['calls']), 2)
            result = ask(FakeClient(['{"sql":null,"reason":"No promotion history."}']), 'Promotions?')
            self.assertEqual(result['status'], 'unsupported')
            self.assertEqual(len(result['calls']), 1)
            result = ask(FakeClient(['{"sql":"DELETE FROM employee","reason":""}']), 'Delete all employees')
            self.assertEqual(result['status'], 'error')
            self.assertEqual(query('SELECT COUNT(*) FROM employee', self.path)['rows'], [[30]])

    def test_report_counts_added_sql_and_unsupported_cases(self):
        cases = [
            {'id': 'first', 'sql': 'SELECT name FROM employee'},
            {'id': 'second', 'sql': 'SELECT role FROM employee'},
            {'id': 'promotions', 'sql': None},
            {'id': 'past_salaries', 'sql': None},
        ]
        metadata = {'started_at': 'test', 'model': 'test', 'pricing': None, 'limit': len(cases)}
        records = [dict(case_id=case['id'], reference_sql=case['sql'],
                        strategy='zero-shot', correct=True,
                        status='answered' if case['sql'] else 'unsupported',
                        question='test', sql=case['sql'], results=None,
                        answer='test', error=None,
                        usage_summary={'estimated_cost_usd': None, 'reported_cost_usd': None,
                                       'prompt_tokens': 0, 'completion_tokens': 0})
                   for case in cases]
        path = Path(self.temp.name) / 'report.md'
        with patch('employee_analytics.experiment.CASES', cases):
            write_report(records, path, metadata)
        report = path.read_text()
        self.assertIn('Correct SQL / 2 | Unsupported recognized / 2 | Completed / 4', report)
        self.assertIn('| zero-shot | 2 | 2 | 4 | 0 |', report)
        self.assertIn('| few-shot | 0 | 0 | 0 | 0 |', report)
        # A saved case snapshot must win over subsequent changes to cases.py.
        metadata['cases'] = cases
        with patch('employee_analytics.experiment.CASES', []):
            write_report(records, path, metadata)
        self.assertEqual(path.read_text(), report)

    def test_report_limit_counts_only_selected_cases(self):
        metadata = {'started_at': 'test', 'model': 'test', 'pricing': None, 'limit': 1}
        path = Path(self.temp.name) / 'limited-report.md'
        write_report([], path, metadata)
        self.assertIn('Correct SQL / 1 | Unsupported recognized / 0 | Completed / 1', path.read_text())


if __name__ == '__main__':
    unittest.main()

