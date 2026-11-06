import subprocess
import sys


class CodeQualityChecker:
    def check(self, filepath):
        issues = []
        result = subprocess.run(
            [sys.executable, '-m', 'flake8', filepath],
            capture_output=True, text=True
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr or result.stdout)
        for line in result.stdout.splitlines():
            if line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    try:
                        lineno = int(parts[1])
                        col_offset = int(parts[2])
                    except ValueError:
                        continue
                    issues.append({
                        'type': 'Lint Issue',
                        'message': line,
                        'lineno': lineno,
                        'col_offset': col_offset - 1
                    })
        return issues
