import os
import io
import pickle
import zipfile
import shutil
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

# Configurations
workspace = r"C:\Users\lenovo\Desktop\San\Fun_Projects\Coral Project"
credentials_path = os.path.join(workspace, "config", "credentials.json")
token_pickle_path = os.path.join(workspace, "config", "token.pickle")
raw_health_dir = os.path.join(workspace, "data", "raw", "health_connect")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    creds = None
    # Check if token exists
    if os.path.exists(token_pickle_path):
        with open(token_pickle_path, 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no valid credentials, run the local auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired Google Drive API token...")
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
                
        if not creds:
            if not os.path.exists(credentials_path):
                print("\n" + "="*80)
                print("❌ CRITICAL: config/credentials.json is missing!")
                print("To connect your Google Drive:")
                print(" 1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print(" 2. Create a project, enable the 'Google Drive API', and create OAuth 2.0 Client credentials.")
                print(" 3. Download the JSON credentials file, rename it to 'credentials.json', and save it to config/credentials.json")
                print("="*80 + "\n")
                return None
                
            print("Launching browser for Google Drive OAuth2 authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save token
        os.makedirs(os.path.dirname(token_pickle_path), exist_ok=True)
        with open(token_pickle_path, 'wb') as token:
            pickle.dump(creds, token)
            
    return build('drive', 'v3', credentials=creds)

def download_latest_backup():
    service = get_drive_service()
    if not service:
        return False
        
    print("Searching Google Drive for latest Health Connect export files...")
    
    # Query files matching "Health Connect" in ZIP or database format, ordered by modified time
    query = "name contains 'Health Connect' and (mimeType = 'application/zip' or name contains '.db')"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, modifiedTime)',
        orderBy='modifiedTime desc'
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        print("❌ No 'Health Connect' files found in your Google Drive!")
        return False
        
    latest_file = files[0]
    file_id = latest_file['id']
    file_name = latest_file['name']
    modified_time = latest_file['modifiedTime']
    
    print(f"Latest Backup Found: {file_name} (Modified: {modified_time})")
    
    # Ensure raw directory exists
    os.makedirs(raw_health_dir, exist_ok=True)
    local_path = os.path.join(raw_health_dir, file_name)
    
    print(f"Downloading to: {local_path} ...")
    
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Progress: {int(status.progress() * 100)}%")
        
    print("Download completed successfully!")
    
    # Extract ZIP if downloaded file is zipped
    if file_name.endswith('.zip'):
        print(f"Extracting {file_name} safely...")
        try:
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(raw_health_dir)
            print("Extracted ZIP contents successfully.")
        except Exception as e:
            print(f"Failed to extract ZIP: {e}")
            return False
            
    return True

if __name__ == '__main__':
    download_latest_backup()
