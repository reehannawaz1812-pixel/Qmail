import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    def __init__(self, smtp_server, smtp_port, imap_server, imap_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.username = username
        self.password = password

    def send_email(self, receiver, subject, body, attachment_path=None, attachment_name=None):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {attachment_name if attachment_name else os.path.basename(attachment_path)}",
                )
                msg.attach(part)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)

    def fetch_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select("inbox")

            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            fetched_emails = []
            # Fetch last 10 emails for now
            for i in range(max(0, len(email_ids)-10), len(email_ids)):
                res, msg_data = mail.fetch(email_ids[i], "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg["Subject"]
                        sender = msg["From"]
                        
                        body = ""
                        attachments = []
                        
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    body = part.get_payload(decode=True).decode()
                                elif "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        attachments.append({
                                            "filename": filename,
                                            "content": part.get_payload(decode=True)
                                        })
                        else:
                            body = msg.get_payload(decode=True).decode()

                        fetched_emails.append({
                            "sender": sender,
                            "subject": subject,
                            "body": body,
                            "attachments": attachments
                        })
            mail.close()
            mail.logout()
            return True, fetched_emails
        except Exception as e:
            return False, str(e)
