# Flutter APK Build and Upload Script

This script automates the process of building Flutter APKs for different flavors, uploading them to Google Drive, organizing them into subfolders based on the build number, and retrieving the public URLs for sharing.

## Prerequisites

1. **Python**: Ensure you have Python installed on your system.
2. **Google Drive API**: Set up the Google Drive API and download the `credentials.json` file.
3. **Flutter**: Make sure you have Flutter installed and configured.

## Setup

### Step 1: Google Drive API Setup

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project.
3. Enable the Google Drive API for your project.
4. Create OAuth 2.0 credentials.
5. Download the `credentials.json` file and place it in the root directory of your flutter project.

### Step 2: Install Required Python Packages

Install the required Python packages using `pip`:

```sh
pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pyyaml

```

### Step 4: Update Script with Main Folder ID
Replace the your_main_folder_id_here in the script with the actual ID of your main Google Drive folder where you want to upload the APKs.

### Step 5: Place the Script
1. Place build_and_upload.py and credentials.json file on root project of flutter application
2. Run python3 build_and_upload.py on terminal to run the script

## Script Usage

# The build_and_upload.py script performs the following tasks:

1. Authenticates with Google Drive.
2. Reads the Applicaiton name, version and build number from pubspec.yaml.
3. Creates a subfolder in Google Drive for the build number if it doesn't exist.
4. Builds APKs for specified Flutter flavors.
5. Uploads the APKs to the appropriate subfolder in Google Drive.
6. Retrieves and prints the public URLs for the uploaded APKs.


## Running the script
```
python3 build_and_upload.py
```
