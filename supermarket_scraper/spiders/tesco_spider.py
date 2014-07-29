"""
Created on Mon Feb  3 13:15:41 2014

@author: onsbigdata
"""

# Standard Python classes
import datetime
import os
import re

# Scrapy-based classes
from scrapy import log
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from supermarket_scraper.items import ProductItem

# Custom classes outside the standard Scrapy stuff
from supermarket_scraper.helpers.store_tree_search import SearchTreeFactory
from supermarket_scraper.helpers.search_settings_helpers import SearchSettingsFactory, TescoSearchSettings
from supermarket_scraper.exceptions.exceptions import TescoSpiderError

class TescoSpider(CrawlSpider):
    """TescoSpider
       ===========
       Main spider for crawling Tecso store website and searching for products.
       Settings for XPaths etc are supplied from SearchSettingsFactory below.
       Search parameters for products are supplied from TescoSearchTreeFactory.
       Spider yields TescoItem for each product line.
       Pipelines exist to post-process data and write it to CSV or MongoDB.
       """
    name = 'tesco' 
    store = "TESCO"
    settings = TescoSearchSettings()
    output_dir = None

    def __init__(self, csv_file=None, *args, **kwargs):
        """Can provide name of input CSV file at runtime e.g.:
        
           scrapy crawl tesco -a csv_file=tesco_input.csv
           
           Input CSV file should be in supermarket_scraper/input directory. 
           If CSV file not specified, defaults to {name}_input.csv 
           e.g. tesco_input.csv.
           
           Output files are written to:
           
           supermarket_scraper/output/[spider name]
           
           Output directory MUST EXIST!
        """
        super(TescoSpider, self).__init__(*args, **kwargs)   
        
        if csv_file:
            self.csv_file = csv_file
        else:
            self.csv_file = self.name + "_input.csv"
            
        # Get URL and XPath settings
        self.settings = SearchSettingsFactory.get_settings(self.store)
        # Get search parameters as tree
        self.search_factory = SearchTreeFactory(self.store, self.csv_file) 
        # Set and check output directory
        self.output_dir = os.path.join('output',self.name)        
        if not (os.path.isdir(self.output_dir)):
            raise TescoSpiderError("Invalid output directory: " + self.output_dir)
        
    def get_searches(self):
        """Returns a tree of searches."""
        if self.csv_file:
            log.msg("Spider: Fetching searches from " + self.csv_file, level=log.DEBUG)            
            return self.search_factory.get_csv_search_tree(self.settings.base_url)
        else:
            #Use some other source for target URLs - database?
            raise TescoSpiderError("Cannot find input file " + self.csv_file)

    def start_requests(self):
        """Generates crawler request for given base URL and parse results."""
        yield Request(url = self.settings.base_url, callback=self.parse_base)                            

    def parse_base(self, response):
        """Parse responses from base URL:
           Overrides Scrapy parser to parse each crawled response.
           Extracts search details from response.
           Looks for next layer of search data (sub 1).
           Yield new Request to fetch required sub-set of data."""
        sel = Selector(response)
        #Get list of searches as a NESTED TREE
        searches = self.get_searches()
        #Find first layer of subordinate data (via nav links)
        #Process each navigation item to find required sub-category
        sub_items = sel.xpath(self.settings.sub1_path)
        for item in sub_items:
            # Check each nav link for the required sub-category
			# Text is returned as a list of strings so join it into a single string
            link_text =  ' '.join(item.xpath('text()').extract())
            # Check search tree i.e. children of top node will be sub1 entries
            for s in searches.children:
                if (link_text == s.name):
                    search_meta = s.as_dict()
                    link_ref = item.xpath('@href').extract()[0]
                    url = link_ref    
                    #print("parse_base: Text matches so use URL:",url)          
                    yield Request(url, meta=search_meta, callback=self.parse_sub1)

    def parse_sub1(self, response):
        """Parse responses from SUB1 URL:
           Overrides Scrapy parser to parse each crawled response.
           Extracts search details from response.
           Looks for next layer of search data (sub 2).
           Yield new Request to fetch required sub-set of data."""
        sel = Selector(response)
        #Find required subordinate data (nav links)
        sub_items = sel.xpath(self.settings.sub2_path)
        for item in sub_items:
            #Check each nav link for the required sub-category
            link_text = ' '.join(item.xpath('text()').extract())
            # Check search tree i.e. children of this node will be sub2 entries
            for s in response.meta['children']:
                #print("Sub 2: Checking link text:", link_text, "against", s['name'])
                if (link_text.encode('utf-16') == s['name'].encode('utf-16')):
                    search_meta = s
                    link_ref = item.xpath('@href').extract()[0]
                    url = link_ref              
                    #print "parse_sub1: Found nav link link: ", url
                    yield Request(url, meta=search_meta, callback=self.parse_sub2)

    def parse_sub2(self, response):
        """Parse responses from SUB2 URL:
           Overrides Scrapy parser to parse each crawled response.
           Extracts search details from response.
           Looks for next layer of search data (sub 2).
           Yield new Request to fetch required sub-set of data."""
        sel = Selector(response)
        #Find required subordinate data (nav links)
        sub_items = sel.xpath(self.settings.sub3_path)
        for item in sub_items:
            #Check each nav link for the required sub-category
            link_text =  ' '.join(item.xpath('text()').extract())
            # Check search tree i.e. children of this node will be sub3 entries
            for s in response.meta['children']:                        
                #print("Sub 3: Checking link text:", link_text, "against", s['name'])
                if (link_text.encode('utf-16') == s['name'].encode('utf-16')):
                    search_meta = s
                    link_ref = item.xpath('@href').extract()[0]
                    url = link_ref              
                    #print "parse_sub2: Found nav link link: ", url
                    yield Request(url, meta=search_meta, callback=self.parse_sub3)

    def parse_sub3(self, response):
        """Parse responses from SUB3 URL:
           Overrides Scrapy parser to parse each crawled response.
           Extracts search details from response.
           Searches for required product within resutls for this sub-category.
           Yield a ProductItem for each product item extracted.
           Yield another request for any "next" page links."""
        sel = Selector(response)
        
        #Find any "next" links for paging and yield Request to next page
        
        next_page = sel.xpath(self.settings.next_page_xpath)
        for page in next_page:
            #Check each nav link for the required sub-category
            next_link_ref = page.xpath('@href').extract()[0]
            #print "Found nav link link: ", url
            yield Request(next_link_ref, meta=response.meta, callback=self.parse_sub3)
            
            
        #Finds product lines
        products = sel.xpath(self.settings.products_xpath) 
        #Process each product line
        # Get details of current search (passed in via response meta data)
        metadata = response.meta['data']
        for product in products:
            # Create an item for each entry
            item = ProductItem()
            item['store'] = self.store
            item['ons_item_no'] =  metadata['ons_item_no']
            item['ons_item_name'] =  metadata['ons_item_name']
            item['product_type'] =  metadata['store_sub3']
            item['search_string'] = metadata['search_terms']
            #Default matches to 1.0 and modify later            
            #item['search_matches'] = 1.0
            #UPPER case product name for storage to make searching easier
            item['product_name'] = (product.xpath(self.settings.product_name_xpath).extract()[0]).upper()   
            # Save price string and convert it to number later
            item['item_price_str'] = product.xpath(self.settings.raw_price_xpath).extract()[0] 
            # Extract raw price by weight or volume
            item['volume_price'] = product.xpath(self.settings.vol_price_xpath).extract()[0] 
            # Add timestamp
            item['timestamp'] = datetime.datetime.now()
            # Get promotion text (if any)
            promo = product.xpath(self.settings.promo_xpath).extract()
            if promo:
                item['promo'] = promo[0]
            else:
                item['promo'] = ''
            # Get short term offer (if any)
            offer = product.xpath(self.settings.offer_xpath).extract()
            if offer:
                item['offer'] = offer[0]
            else:
                item['offer'] = ''
            #Pass the item back
            yield item
