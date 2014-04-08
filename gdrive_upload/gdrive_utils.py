# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 09:20:56 2014

@author: onsbigdata
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def get_authenticated_drive():
    """Connects to GDrive using the pre-installed credentials.
    
       Credentials must first be created online for the Google application via
       the Google console at https://console.developers.google.com/project.
       
       This should be done using the relevant Google user account.
       
       Then copy the ID and secret into settings.yaml where PyDrive can pick it
       up for processing first time.
       
       First time the process runs, you will need to confirm access is
       allowed, and then the credentials will be saved to credentials.json.
       Subsequently, no further interaction should be needed."""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver to handle authentication
    drive = GoogleDrive(gauth)
    return drive

def create_folder(drive, folder, parent='root'):
    """Create folder on Google Drive with given details."""
    params = {'title': folder,
              'mimeType':'application/vnd.google-apps.folder',
              'parents': [{'kind': 'drive#fileLink','id': parent}] }
    data_folder = drive.CreateFile(params)
    data_folder.Upload()
    return data_folder['id']        

def find_folder(drive, folder, parent='root'):
    """Look for given folder in given parent (or root) on given GDrive account."""      
    query = "trashed = false and title ='{fname}' and '{parent}' in parents".format(fname=folder,parent=parent)    
    folder_id = None
    file_list = drive.ListFile({'q':query}).GetList()
    if file_list:
        #assume first entry is our folder 
        folder_id = file_list[0]['id']
    return folder_id        

def get_folder(drive, folder, parent='root'):
    """Look for given folder in given parent (or root) on given GDrive account.
       If it does not yet exist, create it."""      
    folder_id = find_folder(drive, folder, parent)
    if not folder_id:
        #create the required folder
        folder_id = create_folder(drive, folder, parent)
    return folder_id        

def upload_file_as_csv(drive, local_file, fname, parent_id):
    """Copies given CSV file to given GDrive location."""
    #print "*** Uploading file: ",fname
    gfile = drive.CreateFile({'title':fname, 'mimeType':'text/csv',
            'parents': [{'kind': 'drive#fileLink','id': parent_id}]  })
    gfile.SetContentFile(local_file) # Set file contents from local file
    gfile.Upload() # Upload it    

