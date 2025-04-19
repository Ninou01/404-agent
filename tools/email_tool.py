from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
import base64
import os
import pickle


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail():
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)

    # If no (valid) credentials available, do the OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh()
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def send_email(to_email: str, subject: str, body: str, from_name: str = "Maystro Investigator") -> str:
    """
    Sends an email via the authenticated Gmail account.

    Args:
        to_email (str): Recipient's email.
        subject (str): Subject of the email.
        body (str): Plain text body.
        from_name (str): Optional sender name to show in 'From'.

    Returns:
        str: Confirmation message or error.
    """
    try:
        service = authenticate_gmail()

        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_email
        message['From'] = from_name
        message['Subject'] = subject

        # Encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return f"✅ Email sent successfully to {to_email} (Message ID: {send_message['id']})"

    except Exception as e:
        return f"❌ Failed to send email: {e}"
