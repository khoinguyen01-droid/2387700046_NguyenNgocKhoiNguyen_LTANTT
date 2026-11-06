from core import sanitize_sql_input, sanitize_html_input, validate_filename, validate_url

print("=== 1. TEST SQL INJECTION ===")
print("Input: admin' OR '1'='1; DROP TABLE users; --")
print("Output:", sanitize_sql_input("admin' OR '1'='1; DROP TABLE users; --"))

print("\n=== 2. TEST XSS ===")
print("Input: <script>alert('hacked')</script><p>Hello World</p>")
print("Output:", sanitize_html_input("<script>alert('hacked')</script><p>Hello World</p>"))

print("\n=== 3. TEST PATH TRAVERSAL ===")
print("Input '../../etc/passwd':", validate_filename("../../etc/passwd"))
print("Input 'report_2026.pdf':", validate_filename("report_2026.pdf"))

print("\n=== 4. TEST SSRF / URL ===")
print("Input 'http://127.0.0.1/admin':", validate_url("http://127.0.0.1/admin"))
print("Input 'https://hutech.edu.vn':", validate_url("https://hutech.edu.vn"))