# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 11:38:36 2014

@author: onsbigdata
"""
import settings
import os
import gdrive_utils

def process_dir(drive, local_path, foldername, parent):
    """Process each file in this directory:
         Upload each CSV file to target folder.
         If successful, rename local file as filename.uploaded.
         If an error occurs, write error to filename.error.
    """
    #Get target folder ID on Google Drive (create if not already there)
    tgt_folder_id = gdrive_utils.get_folder(drive,foldername,parent)
    #Now find the CSV files we need to process in the local directory
    for fname in os.listdir(local_path):
        if fname.endswith(".csv"):
            try:
                local_file = os.path.join(local_path,fname)
                gdrive_utils.upload_file_as_csv(drive, local_file, fname, tgt_folder_id)
                os.rename(local_file, local_file+'.uploaded')
            except Exception as ex:
                f = open(local_file+'.error', 'w')
                f.write('Exception type:\n'+type(ex))
                f.write('Exception message:\n'+ex.message)
                f.write('Exception args:\n'+ex.args)

def process_outputs():
    """Copies all .csv files from CSV source directories into GDrive account.
       After each CSV file has been copied, the local copy is renamed as
       filename.csv.uploaded so it is not picked up next time.
       If an error occurs while uploading the CSV file to GDrive, the error is 
       written to a file called filename.csv.error for later investigation."""
    # Start in right directory to get OAuth settings
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    os.chdir(dir_path)
    #Get GDrive base folder (creates it in GDrive root folder if not already present)
    drive = gdrive_utils.get_authenticated_drive()
    base_folder_id = gdrive_utils.get_folder(drive,settings.GDRIVE_TARGET_DIR,'root')
    #
    # Find spider-specific folders inside local source folder
    #
    os.chdir(settings.CSV_SOURCE_DIR)
    for d in os.listdir(os.curdir):
        if os.path.isdir(d):
            local_path = os.path.abspath(d)
            process_dir(drive, local_path, d, base_folder_id)
    
def main():
    """Main function."""    
    startdir = os.getcwd()
    process_outputs()
    os.chdir(startdir)

# Runs main() if program called from command line
if __name__ == "__main__":
    main()
    exit()