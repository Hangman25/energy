import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# SMTP server configuration
SMTP_PORT = 587
SMTP_SERVER = "smtp.gmail.com"

def send_email(recipient, csv_buffer, filename):
    """
    Send an email with the CSV attached.

    Parameters:
    - recipient: The recipient's email address.
    - csv_buffer: A BytesIO buffer containing the CSV data.
    - filename: The filename for the CSV attachment.
    """
    try:
        if not isinstance(recipient, str) or "@" not in recipient:
            raise ValueError(f"Invalid email address: {recipient}")

        # Connect to the SMTP server and start TLS encryption
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(st.secrets["EMAIL_FROM"], st.secrets["PSW"])

            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = st.secrets["EMAIL_FROM"]
            msg['To'] = recipient
            msg['Subject'] = "Energy Prediction CSV Attached"

            # Email body
            body = "Please find attached the energy prediction CSV file."
            msg.attach(MIMEText(body, 'plain'))

            # Read CSV data from the buffer
            csv_buffer.seek(0)  # Ensure the pointer is at the beginning
            csv_data = csv_buffer.read()

            # Create and attach the CSV attachment
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(csv_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(attachment)

            # Send the email
            server.sendmail(st.secrets["EMAIL_FROM"], recipient, msg.as_string())

    except Exception as e:
        print(f"Error sending email: {e}")
