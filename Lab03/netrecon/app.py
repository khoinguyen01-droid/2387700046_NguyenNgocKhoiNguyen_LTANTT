from flask import Flask, render_template, request

from modules import (
    port_scanner,
    service_detector,
    banner_grabber,
    network_mapper,
    vuln_checker,
    email_sender
)

from dotenv import load_dotenv

import asyncio
import os


load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    target = request.form["target"].strip()

    ports_text = request.form.get(
        "ports",
        "22,80,443"
    )

    ports = [
        int(p.strip())
        for p in ports_text.split(",")
        if p.strip()
    ]

    mode = request.form.get(
        "mode",
        "all"
    )

    email = request.form.get(
        "email",
        ""
    ).strip()

    result = {
        "scan": None,
        "service": None,
        "banner": None,
        "map": None,
        "vuln": None
    }

    if mode in ["scan", "all"]:
        result["scan"] = asyncio.run(
            port_scanner.async_scan_ports(
                target,
                ports
            )
        )

    if mode in ["service", "all"]:
        result["service"] = (
            service_detector.detect_service(
                target,
                ports
            )
        )

    if mode in ["banner", "all"]:
        result["banner"] = {
            port: banner_grabber.grab_banner(
                target,
                port
            )
            for port in ports
        }

    if mode in ["map", "all"]:
        result["map"] = (
            network_mapper.map_network()
        )

    if mode in ["vuln", "all"]:
        result["vuln"] = (
            vuln_checker.check_vulns(
                ports
            )
        )

    if email:
        body = (
            "Ket qua NetRecon:\n\n"
            f"SCAN:\n{result['scan']}\n\n"
            f"SERVICE:\n{result['service']}\n\n"
            f"BANNER:\n{result['banner']}\n\n"
            f"MAP:\n{result['map']}\n\n"
            f"VULN:\n{result['vuln']}\n"
        )

        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        email_sender.send_email(
            email,
            "Ket qua quet tu NetRecon",
            body,
            smtp_user,
            smtp_pass
        )

    return render_template(
        "result.html",
        result=result
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
