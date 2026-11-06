"""
Unit tests for SecureValidator in core.py
"""

import pytest
from core import (
    SecureValidator,
    validate_email,
    validate_url,
    validate_filename,
    sanitize_sql_input,
    sanitize_html_input,
)


class TestValidateEmail:
    def test_valid_emails(self):
        assert validate_email("user@example.com") is True
        assert validate_email("john.doe+test@sub.domain.org") is True
        assert validate_email("admin_123@company.co.uk") is True

    def test_email_header_injection(self):
        # CRLF injection attempts
        assert validate_email("victim@example.com\r\nBcc: hacker@evil.com") is False
        assert validate_email("victim@example.com\nSubject: Injected") is False
        assert validate_email("victim@example.com\rCc: spam@evil.com") is False
        assert validate_email("user\x00@example.com") is False

    def test_invalid_email_formats(self):
        assert validate_email("") is False
        assert validate_email("not-an-email") is False
        assert validate_email("@missing-user.com") is False
        assert validate_email("missing-domain@") is False
        assert validate_email("user@domain..com") is False
        assert validate_email(None) is False
        assert validate_email(12345) is False
        # Overly long email (> 254 chars)
        assert validate_email("a" * 250 + "@example.com") is False


class TestValidateUrl:
    def test_valid_urls(self):
        # Public domains that resolve
        assert validate_url("https://www.google.com") is True
        assert validate_url("http://example.com/test?param=1") is True

    def test_ssrf_schemes(self):
        # Disallowed schemes
        assert validate_url("file:///etc/passwd") is False
        assert validate_url("gopher://127.0.0.1:6379/_flushall") is False
        assert validate_url("dict://127.0.0.1:11211/stat") is False
        assert validate_url("ftp://example.com/file.txt") is False

    def test_ssrf_internal_ips(self):
        # Loopback
        assert validate_url("http://127.0.0.1") is False
        assert validate_url("http://localhost") is False
        assert validate_url("http://127.0.0.1:8080/admin") is False
        # Private ranges
        assert validate_url("http://10.0.0.1") is False
        assert validate_url("http://192.168.1.1/router") is False
        assert validate_url("http://172.16.0.1") is False
        # AWS / Cloud Metadata IP (link-local)
        assert validate_url("http://169.254.169.254/latest/meta-data/") is False
        # Zero / unspecified IP
        assert validate_url("http://0.0.0.0") is False

    def test_invalid_url_structure(self):
        assert validate_url("not a url") is False
        assert validate_url("") is False
        assert validate_url("http://user:password@google.com") is False  # userinfo disallowed


class TestValidateFilename:
    def test_valid_filenames(self):
        assert validate_filename("report_2026.pdf") is True
        assert validate_filename("avatar-user_1.png") is True
        assert validate_filename("document.docx", allowed_extensions=[".docx", ".pdf"]) is True

    def test_path_traversal(self):
        assert validate_filename("../../etc/passwd") is False
        assert validate_filename("..\\..\\windows\\system32\\cmd.exe") is False
        assert validate_filename("/var/www/index.html") is False
        assert validate_filename("folder/file.txt") is False
        assert validate_filename("..") is False

    def test_null_byte_injection(self):
        assert validate_filename("safe.png\x00.php") is False
        assert validate_filename("safe.png%00.php") is False

    def test_windows_reserved_names(self):
        assert validate_filename("CON.txt") is False
        assert validate_filename("prn.pdf") is False
        assert validate_filename("aux.png") is False
        assert validate_filename("NUL") is False

    def test_extension_filter(self):
        assert validate_filename("script.sh", allowed_extensions=[".jpg", ".png"]) is False
        assert validate_filename("avatar.png", allowed_extensions=["png", "jpg"]) is True


class TestSanitizeSqlInput:
    def test_sql_meta_characters(self):
        malicious = "admin' OR '1'='1"
        sanitized = sanitize_sql_input(malicious)
        assert "''" in sanitized
        assert "admin'' OR ''1''=''1" == sanitized

    def test_stacked_queries_and_comments(self):
        malicious = "1; DROP TABLE users; --"
        sanitized = sanitize_sql_input(malicious)
        assert ";" not in sanitized
        assert "--" not in sanitized
        assert "DROP TABLE users" in sanitized

    def test_block_comments(self):
        malicious = "SELECT /* admin comment */ * FROM accounts"
        sanitized = sanitize_sql_input(malicious)
        assert "/*" not in sanitized
        assert "*/" not in sanitized

    def test_null_bytes(self):
        malicious = "admin\x00' OR 1=1"
        sanitized = sanitize_sql_input(malicious)
        assert "\x00" not in sanitized


class TestSanitizeHtmlInput:
    def test_script_tag_removal(self):
        dirty = "<p>Hello</p><script>alert('XSS')</script>"
        clean = sanitize_html_input(dirty)
        assert "<script>" not in clean
        assert "alert" not in clean
        assert "<p>Hello</p>" in clean

    def test_event_handler_removal(self):
        dirty = '<img src="x" onerror="alert(1)"><b>Bold</b>'
        clean = sanitize_html_input(dirty)
        assert "onerror" not in clean
        assert "<b>Bold</b>" in clean

    def test_javascript_protocol(self):
        dirty = '<a href="javascript:alert(1)">Click me</a>'
        clean = sanitize_html_input(dirty)
        assert "javascript:" not in clean

    def test_safe_tags_preserved(self):
        safe = '<p>This is <strong>important</strong> and <i>italic</i>.</p>'
        assert sanitize_html_input(safe) == safe
