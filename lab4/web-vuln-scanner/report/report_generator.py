class ReportGenerator:
    recommendations = {
        'XSS': 'Encode output by context and apply a Content Security Policy.',
        'SQL Injection': 'Use parameterized queries; never concatenate SQL input.',
        'CSRF': 'Validate CSRF tokens on state-changing requests.',
        'SSRF': 'Allowlist destinations and block access to internal resources.',
    }

    def generate(self, findings_list):
        report = {'vulnerabilities': [], 'checks': []}
        if isinstance(findings_list, dict):
            findings_list = [findings_list]
        for findings in findings_list:
            if isinstance(findings, list):
                items = findings
            elif isinstance(findings, dict):
                items = [findings]
            else:
                raise TypeError('Findings must be dictionaries or lists')
            for item in items:
                if not isinstance(item, dict):
                    raise TypeError('Each finding must be a dictionary')
                finding = dict(item)
                if finding.get('csrf_protected') is True:
                    finding.setdefault('desc', 'CSRF token field found; server validation not verified')
                    report['checks'].append(finding)
                    continue
                description = finding.get('desc', '')
                kind = finding.get('type')
                if not kind:
                    kind = next((name for name in self.recommendations
                                 if name.lower() in description.lower()), 'Unknown')
                finding['type'] = kind
                finding.setdefault('desc', 'Potential vulnerability')
                finding.setdefault('risk', 'LOW')
                finding['risk'] = str(finding['risk']).upper()
                finding.setdefault('recommendation', self.recommendations.get(
                    kind, 'Review the finding in the authorized lab environment.'))
                report['vulnerabilities'].append(finding)
        return report
