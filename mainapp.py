from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# Load the OAuth client credentials
with open("client_secret_251479437235-jd1659flonnr284u763vmrv9ejarjvvp.apps.googleusercontent.com.json") as f:
    client_info = json.load(f)

SCOPES = ["https://www.googleapis.com/auth/adwords"]

# Authenticate the user via OAuth
creds = Credentials.from_authorized_user_file('token.json', SCOPES) if False else None
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_config(client_info, SCOPES)
        creds = flow.run_local_server(port=8080)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

print("Access Token Generated and Saved!")
