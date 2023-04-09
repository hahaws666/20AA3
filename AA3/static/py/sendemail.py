import smtplib
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import  MIMEMultipart
from email.header import  Header


def send_mail(email, name):
    host_server = "smtp.163.com"
    pwd = "TFTGCQSEDWWPJGVV"
    sender = "wszs20031208@163.com"

    rev = email
    title = 'THANK YOU FOR DONATION'
    cont = "Dear "+name+""",\n I hope this letter finds you well. I wanted to express my sincerest gratitude for your generous donation. Your contribution will make a significant impact on our ability to help the people in ukraine.

We believe that every little bit counts, and we are grateful for donors like you who make it possible for us to continue our mission. Your donation will help us support the families under the destruction of the war, and we are honored to have your support.

We understand that there are many deserving organizations out there, and we are humbled that you chose to support us. Your generosity has inspired us to work even harder to make a positive impact in our community.

Once again, thank you for your donation. Your support means the world to us and the people we serve.

Sincerely,

Misty, Andrew and Shuang
"""
    msg = MIMEMultipart()
    msg["Subject"] = Header(title, 'utf-8')
    msg["From"] = sender
    msg["To"] = Header(rev, "utf-8")
    msg.attach(MIMEText(cont, "plain", "utf-8"))
    smpt = SMTP_SSL(host_server)
    smpt.login(sender, pwd)
    smpt.sendmail(sender, rev, msg.as_string())
    smpt.quit()
