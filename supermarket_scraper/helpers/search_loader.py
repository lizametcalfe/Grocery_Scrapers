# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 11:03:33 2014

@author: onsbigdata
"""

import csv
import os

class SearchLoader():
    name = "SearchLoader"
    data_path = ""

    def __init__(self, *args, **kwargs):
        thisloc = os.path.dirname(__file__)
        self.data_path =  os.path.join(thisloc,"..","..","input")


    def get_file_reader(self,fname):
        floc = os.path.join(self.data_path,fname)
        fp = open(floc,'rb')
        return csv.DictReader(fp, dialect='excel', delimiter=',')

    def get_url_queries(self,fname):
        rdr = self.get_file_reader(fname)
        queries = []
        for row in rdr:
            queries.append(row)
        return queries
        
        
