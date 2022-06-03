import os
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "the19Gym@gmail.com"
EMAIL_PASSWORD = "the19Gym4u+me"


def sendReceipt(path, email):

    msg = EmailMessage()
    msg['Subject'] = 'Booking Confirmation'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    msg.set_content('Booking Confirmation.\n\nPlease find your booking receipt attached below.')

    with open(path, 'rb') as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data, maintype = 'application', subtype ='octet-stream', filename = file_name)


    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
