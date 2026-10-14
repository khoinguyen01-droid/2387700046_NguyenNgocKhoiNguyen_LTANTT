from urllib.parse import urlencode
from unittest.mock import Mock, patch

from scanners.xss_scanner import XSSScanner
from scanners.sql_injection_tester import SQLInjectionTester
from scanners.csrf_detector import CSRFDetector
from scanners.ssrf_tester import SSRFTester
from report.report_generator import ReportGenerator


def main():
    # Offline demonstration: no public or internal website is contacted.
    url = 'http://example.com/page?' + urlencode({
        'input': '<script>alert(1)</script>',
        'id': "' OR '1'='1",
        'url': 'http://127.0.0.1/admin',
    })
    html = '<form><input type="hidden" name="csrf_token" value="abc123"/></form>'
    xss = XSSScanner()
    sql = SQLInjectionTester()
    csrf = CSRFDetector()
    ssrf = SSRFTester()
    report_gen = ReportGenerator()
    response = Mock(text='<html><script>alert(1)</script></html>', status_code=200)
    with patch('scanners.xss_scanner.requests.get', return_value=response):
        findings = [xss.scan(url), sql.scan(url), csrf.scan(html), ssrf.scan(url)]
    report = report_gen.generate(findings)
    print('=== Vulnerability Report ===')
    print('Offline lab demonstration; HTTP response is mocked.')
    for vuln in report['vulnerabilities']:
        print(f"Type: {vuln['type']}, Param: {vuln.get('param', 'N/A')}, "
              f"Desc: {vuln['desc']}, Risk: {vuln['risk']}")
    for check in report['checks']:
        print(f"Check: {check['desc']}")


if __name__ == '__main__':
    main()
