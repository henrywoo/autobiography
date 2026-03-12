import os
import hashlib
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# ===== CONFIG =====
SCOPES = ["https://www.googleapis.com/auth/drive"]

CREDENTIALS_FILE = "credentials.json"   # OAuth client file
TOKEN_FILE = "token.json"               # auto-created after first login
MD5_FILE = ".last_upload_md5"           # tracks last uploaded file hash

# My Drive folder ID
FOLDER_ID = "1Pxp89Bv3jkEPS96p9CUZ_TkzdPejrPF4"
# ==================


def get_file_md5(filepath: str) -> str:
    """Calculate MD5 hash of a file."""
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()

def get_credentials():
    """
    Load saved OAuth token or perform one-time device authorization.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )

        # OAuth flow - opens browser or prints URL
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def upload_pdf(local_path: str, base_name: str = "book"):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"{local_path} does not exist")

    # Check MD5 against last upload
    current_md5 = get_file_md5(local_path)
    if os.path.exists(MD5_FILE):
        with open(MD5_FILE, "r") as f:
            last_md5 = f.read().strip()
        if current_md5 == last_md5:
            print(f"Skipped: file unchanged (md5: {current_md5[:8]}...)")
            return

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    # Generate versioned filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{base_name}_{timestamp}.pdf"

    media = MediaFileUpload(
        local_path,
        mimetype="application/pdf",
        resumable=True
    )

    service.files().create(
        body={
            "name": filename,
            "parents": [FOLDER_ID],
        },
        media_body=media,
    ).execute()

    # Save MD5 after successful upload
    with open(MD5_FILE, "w") as f:
        f.write(current_md5)

    print(f"Uploaded: {filename}")


if __name__ == "__main__":
    upload_pdf("book.pdf")


