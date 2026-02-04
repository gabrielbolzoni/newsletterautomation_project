import os.path
import base64
import json
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.


def email_reader():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail messages.
    """
    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("config\credentials\token.json"):
        creds = Credentials.from_authorized_user_file("config\credentials\token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("config\credentials\credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        senders_query = "from:(contato@thenewscc.com.br OR newsletter@filipedeschamps.com.br)" 
        query = f"is:unread {senders_query}"

        results = (
            service.users()
            .messages()
            .list(userId="me", q=query)
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return
        
        news_list = []

        for message in messages:
            # Obtém a mensagem completa uma única vez para economizar chamadas de API (Quota)
            msg_full = service.users().messages().get(userId="me", id=message["id"]).execute()
            payload = msg_full.get('payload', {})
            headers = payload.get('headers', [])

            # Extração robusta do Sender (procurando pelo header 'From')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown")

            # Extração do HTML (considerando que newsletters costumam ter parts)
            parts = payload.get('parts', [])
            if len(parts) > 1:
                html_content = parts[1]['body'].get('data', '')
                html_content_decoded = base64.urlsafe_b64decode(html_content).decode('utf-8')
                
                # 2. Cria a estrutura sender: conteúdo e adiciona à lista
                news_list.append({
                    "sender": sender,
                    "content": html_content_decoded
                })

                # 3. Marca como lido (BatchModify espera uma LISTA de IDs)
                service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': [message['id']], # Deve estar entre colchetes
                        'removeLabelIds': ['UNREAD']
                    }
                ).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")

    return news_list
