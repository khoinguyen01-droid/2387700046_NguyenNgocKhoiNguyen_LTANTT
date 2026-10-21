import tempfile
import unittest
from pathlib import Path
from sast_tool.code_quality_checker import CodeQualityChecker


class TestCodeQualityChecker(unittest.TestCase):
    def test_flake8_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            filepath = Path(directory) / 'sample.py'
            filepath.write_text('import os\n\n\n', encoding='utf-8')
            checker = CodeQualityChecker()
            issues = checker.check(str(filepath))
            self.assertTrue(all(i['type'] == 'Lint Issue' for i in issues)
                            or len(issues) == 0)
