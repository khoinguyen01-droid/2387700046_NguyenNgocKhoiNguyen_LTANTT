import re
import subprocess
import sys
import tempfile


class VirtualSandbox:
    def run_isolated(self, command):
        # A temporary working directory is not an OS sandbox. Accept only
        # harmless echo examples from the lab, and never invoke a shell.
        if not isinstance(command, str):
            raise ValueError('Only echo followed by plain text is allowed.')
        match = re.fullmatch(r'echo ([A-Za-z0-9 ]{1,100})', command)
        if match is None:
            raise ValueError('Only echo followed by plain text is allowed.')
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [sys.executable, '-c', 'import sys; print(sys.argv[1])',
                 match.group(1)],
                cwd=temp_dir, capture_output=True, text=True, timeout=5
            )
        return result.stdout, result.stderr
