import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

def email_alert(toaddr,username,message):
    host = 'smtp.mail.us-east-1.awsapps.com'
    port = '465'
    fromaddr = 'smile@socialmediamacroscope.awsapps.com'

    with open('/home/ubuntu/faculty_trolling/faculty_trolling/config.json', 'r') as f:
        cred = json.load(f)
        password = cred['email_password']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Your Troll Blocker has stopped!'
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg.attach(MIMEText('Dear '
                        + username
                        + ', \nthis email is a reminder that your troll '
                        'blocker has stopped.\nReason:'
                        + message, 'plain'))

    server = smtplib.SMTP_SSL(host, port)
    server.login(fromaddr, password)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()
