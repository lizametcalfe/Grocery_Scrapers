# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 11:26:18 2014

@author: onsbigdata
"""

"""Settings for GDrive Upload processing."""

# Root folder on Google Drive.
# We will create folders inside this folder to hold outputs for each spider.
GDRIVE_TARGET_DIR='prices_upload'

# CSV source dir is the local root for all the output CSV files.
# Each spider writes its output CSV files to its own directory 
# e.g. the "tesco" spider writes to ../output/tesco.
CSV_SOURCE_DIR='../output'

