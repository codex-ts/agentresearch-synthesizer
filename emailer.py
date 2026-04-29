import smtplib
from email.message import EmailMessage
import os

def send_email(sender_email, app_password, receiver_email, file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")
    
    msg = EmailMessage()
    msg["Subject"] = "Research Report"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Please find your research report attached.")

    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="report.pdf")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            print(f"✓ Email sent to {receiver_email}")
    except smtplib.SMTPAuthenticationError:
        raise Exception("Gmail auth failed: Use an App Password, not your regular password")
    except Exception as e:
        raise Exception(f"Email error: {type(e).__name__}: {e}")