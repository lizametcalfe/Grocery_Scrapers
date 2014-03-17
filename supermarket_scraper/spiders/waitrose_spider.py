# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:15:41 2014

@author: onsbigdata
"""

# Standard Python classes
import datetime
import os

# Scrapy-based classes
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from supermarket_scraper.items import ProductItem

# Custom classes outside the standard Scrapy stuff
from supermarket_scraper.helpers.store_tree_search import SearchTreeFactory
from supermarket_scraper.helpers.search_settings_helpers import SearchSettingsFactory, WaitroseSearchSettings
from supermarket_scraper.exceptions.exceptions import WaitroseSpiderError

class WaitroseSpider(CrawlSpider):
    """WaitroseSpider
       ===========
       Main spider for crawling Waitrose website and searching for products.
       Settings for XPaths etc are supplied from SearchSettingsFactory below.
       Search parameters for products are supplied from SearchTreeFactory.
       Spider yields ProductItem for each product line.
       Pipelines exist to post-process data and write it to CSV or MongoDB.
       """
    name = 'waitrose' 
    store = "WAITROSE"
    settings = WaitroseSearchSettings()

    def __init__(self, csv_file=None, output_dir='output', *args, **kwargs):
        """Provide name of CSV file at runtime e.g.:
        
           scrapy crawl waitrose -a csv_file=waitrose_input.csv
           
           Input CSV file should be in data directory. 
           If CSV file not specified, defaults to {name}_input.csv 
           e.g. waitrose_input.csv.
           
           Can also provide an output directory name:
           
           scrapy crawl waitrose -a csv_file=waitrose.csv -a output_dir=output
           
           Directory MUST EXIST!
        """
        super(WaitroseSpider, self).__init__(*args, **kwargs)   
        
        if csv_file:
            self.csv_file = csv_file
        else:
            self.csv_file = self.name + "_input.csv"
            
        # Get URL and XPath settings
        self.settings = SearchSettingsFactory.get_settings(self.store)
        # Get search parameters as tree
        self.search_factory = SearchTreeFactory(self.store, self.csv_file)            
        if not (os.path.isdir(output_dir)):
            raise WaitroseSpiderError("Invalid output directory: " + output_dir)
        else:
            self.output_dir = output_dir                            
        
    def get_searches(self):
        """Returns a LIST of searches."""
        if self.csv_file:
            print "Fetching searches from ", self.csv_file
            return self.search_factory.get_csv_searches()            
        else:
            #Use soem other source for target URLs - database?
            raise WaitroseSpiderError("Cannot find input file " + self.csv_file)

    def start_requests(self):
        """Generates crawler requests for given base URL and parse results."""
        search_list = self.get_searches()
        # Build URLs based on base URL + sub-categories
        for s in search_list:
            search_meta = s.get_meta_map()
            product_url = '/'.join([self.settings.base_url,s.store_sub1,
                    s.store_sub2,
                    s.store_sub3])
            yield Request(url = product_url, meta=search_meta, callback=self.parse_base)                            

    def parse_base(self, response):
        """Parse responses from base URL:
           Overrides Scrapy parser to parse each crawled response.
           Wasitrose apaprently serves all products in a single list so we
           just extract teh product items and yield them for processing."""
        sel = Selector(response)
        metadata = response.meta
        #Finds product lines
        products = sel.xpath(self.settings.products_xpath) 
        #Process each product line
        # Get details of current search (passed in via response meta data)
        for product in products:
            # Create an item for each entry
            item = ProductItem()
            item['store'] = self.store
            item['ons_item_no'] =  metadata['ons_item_no']
            item['ons_item_name'] =  metadata['ons_item_name']
            item['product_type'] =  metadata['store_sub3']
            item['search_string'] = metadata['search_terms']
            #Default matches to 1.0 and modify later            
            item['search_matches'] = 1.0
            #UPPER case product name for storage to make searching easier
            item['product_name'] = (product.xpath(self.settings.product_name_xpath).extract()[0]).upper()   
            # Save price string and convert it to number later
            item['item_price_str'] = product.xpath(self.settings.raw_price_xpath).extract()[0].strip()
            # Volume price not always provided, so we try using volume and item price instead
            vol_price = product.xpath(self.settings.vol_price_xpath).extract()
            item['volume_price'] = item['item_price_str'] + "/" + vol_price[0].strip()                
            # Add timestamp
            item['timestamp'] = datetime.datetime.now()
            # Get promotion text (if any)
            promo = product.xpath(self.settings.promo_xpath).extract() #TODO
            if promo:
                item['promo'] = promo[0]
            else:
                item['promo'] = ''
            # Get short term offer (if any)
            offer = product.xpath(self.settings.offer_xpath).extract() #TODO
            if offer:
                item['offer'] = offer[0]
            else:
                item['offer'] = ''
            #Pass the item back
            yield item
