import unittest
from scanners.ssrf_tester import SSRFTester


class TestSSRFTester(unittest.TestCase):
    def setUp(self):
        self.tester = SSRFTester()

    def test_detect_ssrf(self):
        findings = self.tester.scan('http://example.com/fetch?url=http://127.0.0.1/admin')
        self.assertTrue(any(f['param'] == 'url' and 'SSRF' in f['desc']
                            for f in findings))

    def test_no_ssrf(self):
        findings = self.tester.scan('http://example.com/fetch?url=http://example.com')
        self.assertEqual(findings, [])


if __name__ == '__main__':
    unittest.main()
