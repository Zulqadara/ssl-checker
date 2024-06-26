from urllib.request import ssl, socket
import datetime, smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()
hostnames = [] #Website names
port = '443'

context = ssl.create_default_context()
for hostname in hostnames:
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            certificate = ssock.getpeercert()

    certExpires = datetime.datetime.strptime(certificate['notAfter'], '%b %d %H:%M:%S %Y %Z')

    daysToExpiration = (certExpires - datetime.datetime.now()).days

    print(hostname, daysToExpiration)

    def send_notification(days_to_expire, hostname):

        smtp_port = 587
        smtp_server = os.getenv('SMTP_ENDPOINT')
        sender_email = os.getenv('SMTP_ACCOUNT')
        recipients = []
        password = os.getenv('SMTP_PASSWORD')
        if days_to_expire == 1:
            days = "1 day"
        else:
            days = str(days_to_expire) + " days"
        msg = MIMEText(f"""The TLS Certificate for your {hostname} site expires in {days}""")
        msg['Subject'] = 'Certificate Expiration'
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)

        email_context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=email_context)
            server.login(sender_email, password)
            server.sendmail(sender_email,
                            recipients,
                            msg.as_string())

    if daysToExpiration == 7 or daysToExpiration == 1:
        send_notification(daysToExpiration, hostname)
        pass
