# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 11:38:36 2014

@author: onsbigdata
"""
import settings
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def get_authenticated_drive():
    """Connects to GDrive using the pre-installed credentials.
       Credentials must first be created online for the Google application via
       the Google console at https://console.developers.google.com/project
       This should be done using the relevant Google user account.
       Then copy the ID and secret into settings.yaml where PyDrive can pick it
       up for processing first time.
       First time the process runs, you will need to confirm access is
       allowed, and then the credentials will be saved to credentials.json.
       Subsequently, no further interaction is required."""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication
    drive = GoogleDrive(gauth)
    return drive

def upload_file_as_csv(fname, drive):
    """Copies given CSV file to given GDrive."""
    gfile = drive.CreateFile({'title':fname, 'mimeType':'text/csv'})
    gfile.SetContentFile(fname) # Read file and set it as a content of this instance.
    gfile.Upload() # Upload it

def get_file_list():
    """Get list of CSV files from CSV source directory (see settings.py)."""
    files = []
    for file in os.listdir(settings.CSV_SOURCE_DIR):
        if file.endswith(".csv"):
            files.append(file)
    return files

def process_files():
    """Copies all .csv files in CSV source directory into GDrive account.
       After each CSV file has been copied, the local copy is renamed as
       filename.csv.uploaded so it is not picked up next time.
       If an error occurs while uploading the CSV file to GDrive, the error is 
       written to a file called filename.csv.error for later investigation."""
    #Get an authenticated connection to GDrive
    drive = get_authenticated_drive()
    #Switch to source directory so we know that all files are in the right place
    files = get_file_list()
    os.chdir(settings.CSV_SOURCE_DIR)
    # Try uploading each file in turn.
    #   Success --> rename file as "file.csv.uploaded"
    #   Error --> write any errors to "file.csv.error"
    for fname in files:  
        try:
            upload_file_as_csv(fname, drive)
            os.rename(fname, fname+'.uploaded')
        except Exception as ex:
            f = open(fname+'.error', 'w')
            f.write('Exception type:\n'+type(ex))
            f.write('Exception message:\n'+ex.message)
            f.write('Exception args:\n'+ex.args)
            f.close()
    
def main():
    """Main function."""
    process_files()

# Runs main() if program called from command line
if __name__ == "__main__":
    main()
    exit()