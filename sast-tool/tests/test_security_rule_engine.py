import json
import tempfile
import unittest
from pathlib import Path
from sast_tool.security_rule_engine import SecurityRuleEngine


class TestSecurityRuleEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_file = Path(self.temp_dir.name) / 'temp_rules.json'
        self.rules = [
            {'type': 'Use of eval', 'severity': 'high'},
            {'type': 'Pattern Match', 'severity': 'medium'}
        ]
        self.rules_file.write_text(json.dumps(self.rules), encoding='utf-8')
        self.engine = SecurityRuleEngine(self.rules_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_evaluate(self):
        ast_issues = [{'type': 'Use of eval', 'message': 'msg',
                       'lineno': 1, 'col_offset': 0}]
        pattern_issues = [{'type': 'Pattern Match', 'message': 'msg',
                           'lineno': 2, 'col_offset': 1}]
        results = self.engine.evaluate(ast_issues, pattern_issues)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['severity'], 'high')
        self.assertEqual(results[1]['severity'], 'medium')
