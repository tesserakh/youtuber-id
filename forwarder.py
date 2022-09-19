from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

import os
import re

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    os.getenv('SERVICE_ACCOUNT'), scopes=SCOPES)


def search_file():
    """Search file in drive location
    """
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        files = []
        page_token = None
        while True:
            response = service.files().list(q="mimeType='text/csv'",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print(F'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(f'An error occurred: {error}')
        files = None

    return files


def upload_to_folder(file_to_upload, folder_id):
    """Upload a file to the specified folder and prints file ID, folder ID
    Args: Id of the folder
    Returns: ID of the file uploaded
    """
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        
        # file handling
        file_name = file_to_upload.split('/')[-1]
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_to_upload,
                                mimetype='text/csv',
                                resumable=True)
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(f'File {file_to_upload} has been uploaded.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')


if __name__ == '__main__':
    data_path = 'result'
    files = []
    for file in os.listdir(data_path):
        if re.findall(r'.csv$', file):
            upload_to_folder(os.path.join(data_path, file), os.getenv('DRIVE_PATH_ID'))
    #search_file()

