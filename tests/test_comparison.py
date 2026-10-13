import json
from pathlib import Path
import tempfile
import unittest
from employee_analytics.compare import run_comparison, validate_models
from employee_analytics.html_report import write_html


class FakeClient:
    def __init__(self, model):
        self.model = model

    def pricing(self):
        return {'prompt': '0', 'completion': '0'}

    def complete(self, messages, json_output=False):
        if self.model == 'test/unavailable':
            raise RuntimeError('OpenRouter HTTP 404; test-only error.')
        if json_output:
            unsupported = 'Unknown history?' in messages[-1]['content']
            content = json.dumps({'sql': None if unsupported else 'SELECT COUNT(*) FROM employee',
                                  'reason': 'No history.' if unsupported else ''})
        else:
            content = '<script>alert("test")</script> There are 30 employees.'
        return content, {'model': self.model,
                         'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'cost': 0}}


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'comparison'
        self.cases = [{'id': 'count', 'question': 'Count?', 'sql': 'SELECT COUNT(*) FROM employee'},
                      {'id': 'history', 'question': 'Unknown history?', 'sql': None}]

    def test_arbitrary_models_generate_complete_escaped_html_and_evidence(self):
        models = ['test/one', 'test/two', 'test/three']
        comparison = run_comparison(models, self.cases, self.directory, FakeClient)
        self.assertEqual(comparison['status'], 'finished')
        self.assertEqual(len(comparison['runs']), 3)
        for run in comparison['runs']:
            self.assertEqual(len(run['records']), 4)
            self.assertTrue(all(r['correct'] for r in run['records']))
            self.assertTrue((self.directory / run['directory'] / 'examples.jsonl').exists())
        html = (self.directory / 'index.html').read_text()
        self.assertIn('12 / 12', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>alert', html)
        self.assertIn('id="model-filter"', html)
        saved = json.loads((self.directory / 'comparison.json').read_text())
        # Rendering uses the saved selection, without network or current config.
        write_html(saved, self.directory / 'rebuilt.html')
        self.assertEqual((self.directory / 'rebuilt.html').read_text(), html)
        with self.assertRaises(FileExistsError):
            run_comparison(models, self.cases, self.directory, FakeClient)

    def test_model_failure_does_not_stop_other_models_or_hide_pending_cases(self):
        comparison = run_comparison(['test/unavailable', 'test/working'], self.cases,
                                    self.directory, FakeClient)
        self.assertEqual(comparison['status'], 'finished with errors')
        self.assertEqual(len(comparison['runs'][0]['records']), 1)
        self.assertEqual(len(comparison['runs'][1]['records']), 4)
        html = (self.directory / 'index.html').read_text()
        self.assertIn('Pending', html)
        self.assertIn('OpenRouter HTTP 404', html)
        self.assertIn('5 / 8', html)

    def test_model_configuration_validation(self):
        validate_models(['test/only-one'])
        for models in ([], [''], ['test/one', 'test/one']):
            with self.subTest(models=models), self.assertRaises(ValueError):
                validate_models(models)


if __name__ == '__main__':
    unittest.main()
