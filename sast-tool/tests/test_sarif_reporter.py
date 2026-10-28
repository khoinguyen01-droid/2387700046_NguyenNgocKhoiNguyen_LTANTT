import tempfile
import unittest
from pathlib import Path
from sast_tool.sarif_reporter import SarifReporter


class TestSarifReporter(unittest.TestCase):
    def test_generate_report(self):
        issues = [{
            'type': 'Test',
            'message': 'Test message',
            'lineno': 1,
            'col_offset': 0
        }]
        reporter = SarifReporter()
        with tempfile.TemporaryDirectory() as directory:
            output_file = Path(directory) / 'test_report.sarif'
            reporter.generate_report(issues, str(output_file))
            self.assertTrue(output_file.exists())
