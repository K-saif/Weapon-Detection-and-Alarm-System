import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

def mail_bot(path):
    # Connection with the server
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    server.login('2020ca30f@sigce.edu.in', 'pwhgdhumldeybbae')

    # Creation of the MIMEMultipart Object
    message = MIMEMultipart()

    # Setup of MIMEMultipart Object Header
    message['From'] = 'khansf466@gmail.com'
    message['To'] = '2020ca30f@sigce.edu.in'
    message['Subject'] = "weapon detected in your property"

    # Creation of a MIMEText Part
    textPart = MIMEText("pistol detected.\n\nAttached is the image of detected weapon", 'plain')

    # Creation of a MIMEApplication Part
    filename = path
    filePart = MIMEApplication(open(filename, "rb").read(), Name=filename)
    filePart["Content-Disposition"] = 'attachment; filename="%s' % filename

    # Parts attachment
    message.attach(textPart)
    message.attach(filePart)

    # Send Email and close connection
    server.send_message(message)
    server.quit()
