import smtplib
from email.message import EmailMessage


def send_email(
    receiver_email,
    subject,
    body,
    smtp_user,
    smtp_pass
):
    if not smtp_user or not smtp_pass:
        print("[!] SMTP_USER/SMTP_PASS not configured.")
        return False

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = receiver_email

    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                smtp_user,
                smtp_pass
            )

            smtp.send_message(msg)

        print(f"[+] Email sent to {receiver_email}")
        return True

    except Exception as e:
        print(f"[-] Email failed: {e}")
        return False