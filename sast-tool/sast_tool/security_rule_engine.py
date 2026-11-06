import json
from pathlib import Path


class SecurityRuleEngine:
    def __init__(self, rules_file=None):
        if rules_file is None:
            rules_file = Path(__file__).resolve().parent.parent / 'rules' / 'default_rules.json'
        with open(rules_file, encoding='utf-8') as f:
            self.rules = json.load(f)

    def evaluate(self, ast_issues, pattern_issues):
        issues = []
        for issue in ast_issues + pattern_issues:
            for rule in self.rules:
                if rule['type'] in issue['type']:
                    issue['severity'] = rule.get('severity', 'medium')
                    issues.append(issue)
        return issues
