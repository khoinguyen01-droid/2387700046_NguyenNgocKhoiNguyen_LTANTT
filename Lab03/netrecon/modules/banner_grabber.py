import socket
import logging
from datetime import datetime


logging.basicConfig(
    filename="netrecon.log",
    level=logging.INFO
)


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{now}] {msg}")


def grab_banner(ip, port):
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(2)

    try:
        sock.connect((ip, port))

        try:
            banner = sock.recv(1024).decode(
                errors="ignore"
            ).strip()

        except socket.timeout:
            banner = "Connected, but no banner returned"

        log(f"{ip}:{port} Banner: {banner}")

        return banner

    except Exception as e:
        result = f"Failed to grab banner: {e}"
        log(result)
        return result

    finally:
        sock.close()