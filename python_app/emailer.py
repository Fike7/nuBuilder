# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from . import database

def get_smtp_settings():
    """
    Fetches SMTP settings from the zzzzsys_setup table in the database.
    """
    sql = "SELECT * FROM zzzzsys_setup LIMIT 1"
    settings = database.run_query(sql, fetch="one")

    if not settings:
        return None

    port = settings.get('set_smtp_port', 25)
    secure = None
    if port == 587:
        secure = 'tls'
    elif port == 465:
        secure = 'ssl'

    return {
        'username': settings.get('set_smtp_username'),
        'password': settings.get('set_smtp_password'),
        'host': settings.get('set_smtp_host', '127.0.0.1'),
        'port': port,
        'use_authentication': settings.get('set_smtp_use_authentication') == '1',
        'from_address': settings.get('set_smtp_from_address'),
        'from_name': settings.get('set_smtp_from_name'),
        'secure': secure
    }

def send_email(to_list, subject, body, from_address=None, from_name=None, is_html=False, attachments=None, cc_list=None, bcc_list=None):
    """
    Constructs and sends an email using the configured SMTP settings.

    Args:
        to_list (list): A list of recipient email addresses.
        subject (str): The email subject.
        body (str): The email body content.
        from_address (str, optional): The sender's email address. Overrides default.
        from_name (str, optional): The sender's name. Overrides default.
        is_html (bool, optional): Whether the body content is HTML.
        attachments (dict, optional): A dictionary of {filename: file_data} for attachments.
        cc_list (list, optional): A list of CC recipients.
        bcc_list (list, optional): A list of BCC recipients.

    Returns:
        tuple: A tuple containing (bool: success, str: message).
    """
    settings = get_smtp_settings()
    if not settings:
        return False, "SMTP settings not found in the database."

    sender_addr = from_address or settings.get('from_address')
    sender_name = from_name or settings.get('from_name')

    if not sender_addr:
        return False, "Sender email address is not configured."

    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <{sender_addr}>"
    msg['To'] = ", ".join(to_list)
    msg['Subject'] = subject

    if cc_list:
        msg['Cc'] = ", ".join(cc_list)

    all_recipients = to_list + (cc_list or []) + (bcc_list or [])

    msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

    if attachments:
        for filename, file_data in attachments.items():
            part = MIMEBase('application', 'octet-stream')
            # The file data from a browser upload might be base64 encoded
            try:
                import base64
                part.set_payload(base64.b64decode(file_data))
            except Exception:
                part.set_payload(file_data) # Assume raw bytes if decode fails

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)

    try:
        server = None
        if settings['secure'] == 'ssl':
            server = smtplib.SMTP_SSL(settings['host'], settings['port'], timeout=10)
        else:
            server = smtplib.SMTP(settings['host'], settings['port'], timeout=10)
            if settings['secure'] == 'tls':
                server.starttls()

        if settings.get('use_authentication'):
            server.login(settings['username'], settings['password'])

        server.sendmail(sender_addr, all_recipients, msg.as_string())
        server.quit()
        return True, "Email sent successfully."

    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
