# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:04:53 2014

@author: onsbigdata
"""

from nose.tools import *
from scrapy_tesco.helpers.search_loader import SearchLoader
from scrapy_tesco.spiders.tesco_spider2 import TescoSpider2
    
class TestScrapyTesco():
 
    def setup(self):
        self.loader = SearchLoader()    

# 
#    def teardown(self):
#        print ("teardown() after each test method")
    
    @classmethod
    def setup_class(cls):
        pass

# 
#    @classmethod
#    def teardown_class(cls):
#        print ("teardown_class() after any methods in this class")

    def __init__(self, *args, **kwargs):
        #Specify CSV file name
        self.test_csv_file = "tesco2_input.csv"
        
    def test_search_loader_instance(self):
        assert_equals(self.loader.name, "SearchLoader")

    def test_get_file_reader(self):
        reader = self.loader.get_file_reader(self.test_csv_file)        
        lines = list(reader)
        assert len(lines) > 0

    def test_get_search_queries(self):
        qs = self.loader.get_url_queries(self.test_csv_file)
        assert len(qs) > 0

    def test_search_query_format(self):
        qs = self.loader.get_url_queries(self.test_csv_file)
        q = qs[0]
        assert 'ons_item_no' in q
        assert q['ons_item_no'] > 0
        assert 'ons_item_name' in q
        assert len(q['ons_item_name']) > 0

    def test_search_url_format(self):
        qs = self.loader.get_url_queries(self.test_csv_file)
        q = qs[0]
        assert 'ons_item_no' in q
        assert (q['base_url']).startswith("http")

    def test_spider_creation(self):
        boris = TescoSpider2()
        # Check default spider and input CSV file names
        assert_equals (boris.name, 'tesco2')
        assert_equals (boris.csv_file, "tesco2_input.csv")
        
    def test_spider_search_params(self):
        boris = TescoSpider2()
        ss = boris.get_searches()
        # Did we get anything back?
        assert ss != None
        assert len(ss) > 0
        s0 = ss[0]
        assert_equals(s0.base_url, "http://www.tesco.com/groceries/")

    def test_spider_search_meta(self):
        boris = TescoSpider2()
        ss = boris.get_searches()
        # Did we get anything back?
        assert ss != None
        assert len(ss) > 0
        s0 = ss[0]
        #Check meta data map against properties for this search
        meta = s0.get_meta_map()        
        assert_equals(meta.get('ons_item_no'),s0.ons_item_no)
        assert_equals(meta.get('ons_item_name'),s0.ons_item_name)
        assert_equals(meta.get('base_url'), s0.base_url)
        assert_equals(meta.get('base_cat'), s0.base_cat)
        assert_equals(meta.get('store_sub1'),s0.store_sub1)
        assert_equals(meta.get('store_sub2'),s0.store_sub2)
        assert_equals(meta.get('store_sub3'),s0.store_sub3)
        assert_equals(meta.get('search_terms'),s0.search_terms)


        
        
