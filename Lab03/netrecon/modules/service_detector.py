import subprocess
import logging
from datetime import datetime

logging.basicConfig(filename='netrecon.log', level=logging.INFO)


def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"[{now}] {msg}")


def detect_service(ip, ports):
    if not ports:
        return "No ports provided."

    ports_str = ','.join(str(p) for p in ports)
    cmd = ["nmap", "-sT", "-sV", "--version-light", "-p", ports_str, ip]

    log(f"Running service detection on {ip}:{ports_str}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="ignore",
            timeout=60
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        log(output)
        return output

    except subprocess.TimeoutExpired:
        message = "Service detection timed out after 60 seconds."
        log(message)
        return message

    except FileNotFoundError:
        message = "Nmap executable was not found."
        log(message)
        return message

    except Exception as e:
        message = f"Service detection error: {e}"
        log(message)
        return message