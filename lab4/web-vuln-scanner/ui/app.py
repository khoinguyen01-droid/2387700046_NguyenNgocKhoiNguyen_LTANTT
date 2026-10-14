import os
import sys
from urllib.parse import urlsplit

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from flask import Flask, render_template, request
from scanners.xss_scanner import XSSScanner
from scanners.sql_injection_tester import SQLInjectionTester
from scanners.csrf_detector import CSRFDetector
from scanners.ssrf_tester import SSRFTester
from report.report_generator import ReportGenerator

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        options = request.form.getlist('scanner')
        try:
            parsed = urlsplit(url)
            valid_url = (parsed.scheme in ('http', 'https') and parsed.hostname
                         and not parsed.username and not parsed.password)
            parsed.port
        except ValueError:
            valid_url = False
        if not valid_url:
            return render_template('index.html', error='Nhập URL HTTP/HTTPS hợp lệ, không chứa thông tin đăng nhập.'), 400
        if not options or any(option not in ('xss', 'sql', 'csrf', 'ssrf') for option in options):
            return render_template('index.html', error='Chọn ít nhất một công cụ hợp lệ.'), 400
        results = []
        errors = []
        if 'xss' in options:
            xss = XSSScanner()
            results.append(xss.scan(url))
            errors.extend(xss.errors)
        if 'sql' in options:
            results.append(SQLInjectionTester().scan(url))
        if 'csrf' in options:
            try:
                response = requests.get(url, timeout=5, allow_redirects=False)
                response.raise_for_status()
                if 300 <= response.status_code < 400:
                    errors.append('CSRF: không theo redirect; chưa phân tích trang đích.')
                else:
                    results.append(CSRFDetector().scan(response.text))
            except requests.RequestException as exc:
                errors.append(f'Không lấy được HTML để kiểm tra CSRF: {exc}')
        if 'ssrf' in options:
            results.append(SSRFTester().scan(url))
        report = ReportGenerator().generate(results)
        return render_template('result.html', report=report, errors=errors)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
