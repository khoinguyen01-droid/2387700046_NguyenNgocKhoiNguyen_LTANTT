from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests


class XSSScanner:
    def __init__(self):
        self.payloads = ["<script>alert(1)</script>", "'><svg/onload=alert(1)>"]
        self.errors = []

    def scan(self, url):
        """Send lab payloads only to a target the operator is authorized to test."""
        results = []
        self.errors = []
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            raise ValueError('URL must use HTTP or HTTPS and include a host')
        for payload in self.payloads:
            params = [(key, value) for key, value in
                      parse_qsl(parsed.query, keep_blank_values=True) if key != 'q']
            params.append(('q', payload))
            test_url = urlunsplit(parsed._replace(query=urlencode(params), fragment=''))
            try:
                resp = requests.get(test_url, timeout=5, allow_redirects=False)
                resp.raise_for_status()
                if 300 <= resp.status_code < 400:
                    self.errors.append('XSS: redirect not followed; scan incomplete')
                    continue
                if payload in resp.text:
                    results.append({
                        'type': 'XSS',
                        'param': 'q',
                        'payload': payload,
                        'url': test_url,
                        'desc': 'Potential reflected XSS: payload reflected in response',
                        'risk': 'HIGH',
                    })
            except requests.RequestException as exc:
                self.errors.append(f'XSS request failed: {exc}')
        return results
