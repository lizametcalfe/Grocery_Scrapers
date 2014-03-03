# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:04:53 2014

@author: onsbigdata
"""

from nose.tools import *
from scrapy_tesco.helpers.url_loader import UrlLoader
from scrapy_tesco.helpers.store_product_search import TescoProductSearch
import os
import csv
import urllib
    
class TestScrapyTesco():
 
    def setup(self):
        print ("setup() before each test method")
        self.loader = UrlLoader()    

# 
#    def teardown(self):
#        print ("teardown() after each test method")
    
    @classmethod
    def setup_class(cls):
        print ("Create tesco_test.csv in /data directory")
        thisloc = os.path.dirname(__file__)
        data_path =  os.path.join(thisloc,"..","scrapy_tesco","data")   
        fp = os.path.join(data_path,"tesco_test.csv")
        ofile  = open(fp, "wb")
        writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        row = ["product_type","product_name","qparams"]
        writer.writerow(row)
        row = ["DAIRY","BUTTER","butter 250g"]
        writer.writerow(row)
        row = ["DAIRY","MILK","semi-skimmed milk"]
        writer.writerow(row)
        row = ["MEAT","BACON","bacon 250g"]
        writer.writerow(row)
        row = ["BREAD","WHITE LOAF","white sliced loaf 800g"]
        writer.writerow(row)
        ofile.close()

# 
#    @classmethod
#    def teardown_class(cls):
#        print ("teardown_class() after any methods in this class")

    def __init__(self, *args, **kwargs):
        #Specify CSV file name
        self.test_csv_file = "tesco_test.csv"
        
    def test_url_loader_instance(self):
        assert_equals(self.loader.name, "UrlLoader")

    def test_get_file_reader(self):
        reader = self.loader.get_file_reader(self.test_csv_file)        
        lines = list(reader)
        assert len(lines) > 0

    def test_get_url_queries(self):
        qs = self.loader .get_url_queries(self.test_csv_file)
        assert len(qs) > 0

    def test_url_query_format(self):
        qs = self.loader .get_url_queries(self.test_csv_file)
        q = qs[0]
        assert 'prodtype' in q
        assert 'qparams' in q

    def testInitTescoProductSearch(self):
        qp = "white%20loaf%20800g"
        pt = "BREAD"
        pn = "white sliced loaf 800g"
        sps =  TescoProductSearch(pt,pn) 
        sps.set_query_paramstr(qp)
        assert "TESCO" == sps.store
        assert sps.query_paramstr == urllib.quote(qp.encode('utf8'))
        assert pt == sps.product_type
        assert pn == sps.product_name
        

        
        
