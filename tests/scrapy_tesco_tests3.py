# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:04:53 2014

@author: onsbigdata
"""

from nose.tools import *
from scrapy_tesco.helpers.search_loader import SearchLoader
from scrapy_tesco.helpers.store_tree_search import *

from scrapy_tesco.spiders.tesco_spider3 import TescoSpider3

def walk_tree(tree,n=0):
    s = "\n" + ("." * n)+"Name = " + tree.name
    for s1 in tree.children:
        s+= walk_tree(s1,n+1)
    return s
 
class TestScrapyTesco3():
 
    def setup(self):
        print "Setup for TestScrapyTesco3"
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
        self.test_csv_file = "tesco3_input.csv"


    def test_search_tree(self):
        factory = TescoSearchTreeFactory(self.test_csv_file)
        tree = factory.get_csv_search_tree("Test")
        s = walk_tree(tree)
        assert (len(s) > 0)

    def test_tree2dict(self):
        factory = TescoSearchTreeFactory(self.test_csv_file)
        tree = factory.get_csv_search_tree("Test")
        d = tree.as_dict()
        assert d['name'] == "Test"
        assert len(d['children']) > 0
        
