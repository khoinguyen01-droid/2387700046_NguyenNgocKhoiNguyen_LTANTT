import asyncio
import logging
from datetime import datetime


logging.basicConfig(
    filename="netrecon.log",
    level=logging.INFO
)


def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{now}] {message}")


async def scan_port(target, port, semaphore):
    async with semaphore:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port),
                timeout=1
            )

            print(f"[+] {port}/tcp open")
            log(f"Port {port} is open on {target}")

            writer.close()
            await writer.wait_closed()

            return port

        except Exception:
            return None


async def async_scan_ports(target, ports, rate_limit=100):
    semaphore = asyncio.Semaphore(rate_limit)

    tasks = [
        scan_port(target, port, semaphore)
        for port in ports
    ]

    results = await asyncio.gather(*tasks)

    open_ports = [
        port
        for port in results
        if port is not None
    ]

    return open_ports