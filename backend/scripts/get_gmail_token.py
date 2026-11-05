import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

client_config = {
    "web": {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8080/"],
    }
}

flow = InstalledAppFlow.from_client_config(
    client_config, scopes=["https://www.googleapis.com/auth/gmail.send"]
)
credentials = flow.run_local_server(
    port=8080, access_type="offline", prompt="consent"
)

print(credentials.refresh_token)