"""
Created on Mon Feb  3 13:15:41 2014

@author: onsbigdata
"""

# Standard Python classes
import datetime
import os

# Scrapy-based classes
from scrapy import log
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
    output_dir = None
    settings = WaitroseSearchSettings()

    def __init__(self, csv_file=None, *args, **kwargs):
        """Can provide name of input CSV file at runtime e.g.:
        
           scrapy crawl waitrose -a csv_file=waitrose_input.csv
           
           Input CSV file should be in data directory. 
           If CSV file not specified, defaults to {name}_input.csv 
           e.g. waitrose_input.csv.
           
           Output files are written to:
           
           supermarket_scraper/output/[spider name]
           
           Output directory MUST EXIST!
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
        # Set and check output directory
        self.output_dir = os.path.join('output',self.name)        
        if not (os.path.isdir(self.output_dir)):
            raise WaitroseSpiderError("Invalid output directory: " + self.output_dir)
        
    def get_searches(self):
        """Returns a LIST of searches. We don't need to nest searches here
           because Waitrose website allows us to construct URLs directly,
           instead of having to navigate through several layers of menus."""
        if self.csv_file:
            log.msg("Spider: Fetching searches from " + self.csv_file, level=log.DEBUG)            
            return self.search_factory.get_csv_searches()            
        else:
            #Use some other source for target URLs - database?
            raise WaitroseSpiderError("Cannot find input file " + self.csv_file)

    def start_requests(self):
        """Generates crawler requests for given base URL and parses results."""
        search_list = self.get_searches()
        # Build URLs based on base URL + sub-categories
        for s in search_list:
            search_meta = {}
            product_url = ''
            search_meta = s.get_meta_map()
            product_url = '/'.join([self.settings.base_url,
                                    s.store_sub1,
                                    s.store_sub2,
                                    s.store_sub3])+'/'
            log.msg("Spider: start_requests() yielding URL: "+product_url, level=log.DEBUG)
            yield Request(url = product_url, meta=search_meta)

    def parse_start_url(self, response):
        """Default function to parse responses from base URL:
           Waitrose serves products in a single list, but we cannot scroll
           through them and there is no 'Next page' link, so we just extract
           the first set of up to 24 product items and yield them for processing."""
           
        # Get details of current search (passed in via response meta data)
        metadata = response.meta
        #Find product lines
        sel = Selector(response)
        products = sel.xpath(self.settings.products_xpath) 
        #Process each product line
        log.msg("Spider: parsing response for URL: " +
                response.url + 
                " for ONS item " + 
                metadata['ons_item_name'], level=log.DEBUG)
        for product in products:
            # Create an item for each entry
            item = ProductItem()
            #UPPER case product name for storage to make searching easier
            try:
                item['product_name'] = (product.xpath(self.settings.product_name_xpath).extract()[0]).upper()
            except:
                continue

            log.msg("Spider: Response for URL: " +
                response.url + 
                " found " + item['product_name'].encode('utf-16') 
                , level=log.DEBUG)
            try: 
                item['store'] = self.store
                item['ons_item_no'] =  metadata['ons_item_no']
                item['ons_item_name'] =  metadata['ons_item_name']
                item['product_type'] =  metadata['store_sub3']
                item['search_string'] = metadata['search_terms']

            except:
                continue
            #Default matches to 1.0 and modify later    

            try:        
                item['search_matches'] = 1.0
            # Save price string and convert it to number later
            	item['item_price_str'] = product.xpath(self.settings.raw_price_xpath).extract()[0].strip()
            	x = item['item_price_str'][0] 
            	print('test', x)
                #pos = item['item_price_str'].index('\xc2')
                	#item['item_price_str'] = item['item_price_str'][:].strip()
                	#print(item['item_price_str'][4])
                if item['item_price_str'][0] == 'N':
                	item['item_price_str'] = item['item_price_str'][3:].strip()
                else:
                	item['item_price_str'] = item['item_price_str'][:].strip()            

            # Try getting the volume and putting it on the end of the product name
                volume = product.xpath(self.settings.volume_xpath).extract()
                if volume:
                    item['product_name'] = item['product_name'] + " " + volume[0].strip().upper()
            except:
                continue
                
            # Waitrose volume price not always provided, so if it is not there, 
            # we try using volume and item price instead. 
            try:
                item['volume_price'] = ''                       
                vol_price = product.xpath(self.settings.vol_price_xpath).extract()
                if vol_price:
                    #Allow for e.g. "1.25 per litre" instead of "1.25/litre"
                    item['volume_price'] = (vol_price[0].strip()).replace("per","/")
                else:
                    item['volume_price'] = item['item_price_str'] + "/" + volume[0].strip()

                # Add timestamp
                item['timestamp'] = datetime.datetime.now()
                # Get promotion text (if any) NOT YET IMPLEMENTED
                item['promo'] = ''
                if self.settings.promo_xpath:
                    promo = product.xpath(self.settings.promo_xpath).extract() #TODO
                    if promo:
                        item['promo'] = promo[0]
                # Get short term offer (if any) NOT YET IMPLEMENTED
                item['offer'] = ''
                if self.settings.offer_xpath:
                    offer = product.xpath(self.settings.offer_xpath).extract() #TODO
                    if offer:
                        item['offer'] = offer[0]
            except:
                continue
            #Pass the item back
            yield item



