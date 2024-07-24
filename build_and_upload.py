import os
import subprocess
import yaml
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

MAIN_FOLDER_ID = 'XXXXXXXXXXXXX'  # Replace with your main Google Drive folder ID

def authenticate():
    """Authenticate the user and return the Drive API service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            try:
                creds = pickle.load(token)
            except (pickle.UnpicklingError, EOFError) as e:
                print("Error loading token.pickle, it might be corrupted.")
                os.remove('token.pickle')
                print("Deleted corrupted token.pickle. Please run the script again to re-authenticate.")
                exit(1)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def get_build_number():
    """Extract the build number from pubspec.yaml."""
    with open('pubspec.yaml', 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            version = data['version'].split('+')[0]
            app_name=data['name']
            build_number = data['version'].split('+')[1]
            return app_name,version,build_number
        except yaml.YAMLError as exc:
            print(exc)
            return None

def create_drive_folder(service, folder_name, parent_id):
    """Create a folder in Google Drive."""
    file_metadata = {
        'name': folder_name,
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def get_folder_id(service, folder_name, parent_id):
    """Get the folder ID from Google Drive, create it if it doesn't exist."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if not items:
        print(f"Creating folder: {folder_name}")
        return create_drive_folder(service, folder_name, parent_id)
    else:
        return items[0]['id']

def build_apk(flavor):
    """Build APK for the given flavor."""
    cmd = f"flutter build apk --release --flavor {flavor} "
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    print(result.stdout.decode())

def upload_to_drive(service, file_path, file_name, folder_id):
    """Upload file to Google Drive and get the public URL."""
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/vnd.android.package-archive')
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink, webContentLink').execute()
    print(f'Uploaded File ID: {file.get("id")}')
    print(f'View Link: {file.get("webViewLink")}')
    print(f'Download Link: {file.get("webContentLink")}')
    return file.get("webViewLink"), file.get("webContentLink")

def main():
    # Authenticate and create the service
    service = authenticate()

    # Get the build number from pubspec.yaml
    app_name,version,build_number = get_build_number()
    if not build_number:
        print("Failed to get build number from pubspec.yaml")
        return

    # Get or create the folder ID for the build number within the main folder
    folder_id = get_folder_id(service, version, MAIN_FOLDER_ID)
    if not folder_id:
        print(f"Failed to get or create folder for build number: {build_number}")
        return

    # Define your flavor here
   # flavors = ["development", "staging", "production"]
    flavors = ["dev"]
    for flavor in flavors:
        print(f"Building APK for flavor: {flavor}")
        build_apk(flavor)
        
        apk_path = os.path.join("build", "app", "outputs", "flutter-apk", f"app-{flavor}-release.apk")
        apk_name = f"{app_name}-{flavor} v{version}({build_number}).apk"
        print(f"Uploading {apk_path} to Google Drive")
        
        view_link, download_link = upload_to_drive(service, apk_path, apk_name, folder_id)
        print(f"Public View Link: {view_link}")
        print(f"Public Download Link: {download_link}")

if __name__ == '__main__':
    main()

