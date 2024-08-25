from email.message import EmailMessage
import smtplib

def set_email_content(subject, body, user_email):
    """set email content, pass to send_email"""
    sent_from = "Cap Companion"
    msg = EmailMessage()
    msg["Subject"], msg["To"], msg["From"] = subject, user_email, sent_from
    msg.set_content(body)
    send_email(msg)

def send_email(msg):
    """send email to the users inputted email address and confirms to user in GUI"""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_username = "email.notification.automation@gmail.com"
    smtp_password = "Ynhxkxhowrxuipqi"
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()