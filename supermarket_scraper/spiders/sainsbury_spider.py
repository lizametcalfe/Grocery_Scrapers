# -*- coding: utf-8 -*-
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
from supermarket_scraper.helpers.search_settings_helpers import SearchSettingsFactory, SainsburySearchSettings
from supermarket_scraper.exceptions.exceptions import SainsburySpiderError

class SainsburySpider(CrawlSpider):
    """SainsburySpider
       ===========
       Main spider for crawling Tecso store website and searching for products.
       Settings for XPaths etc are supplied from SearchSettingsFactory below.
       Search parameters for products are supplied from sainsburySearchTreeFactory.
       Spider yields sainsburyItem for each product line.
       Pipelines exist to post-process data and write it to CSV or MongoDB.
       """
    name = 'sainsbury' 
    store = "SAINSBURY"
    settings = SainsburySearchSettings()
    output_dir = None

    def __init__(self, csv_file=None, *args, **kwargs):
        """Can provide name of input CSV file at runtime e.g.:
        
           scrapy crawl sainsbury -a csv_file=sainsbury_input.csv
           
           Input CSV file should be in supermarket_scraper/input directory. 
           If CSV file not specified, defaults to {name}_input.csv 
           e.g. sainsbury_input.csv.
           
           Output files are written to:
           
           supermarket_scraper/output/[spider name]
           
           Output directory MUST EXIST!
        """
        super(SainsburySpider, self).__init__(*args, **kwargs)   
        
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
            raise SainsburySpiderError("Invalid output directory: " + self.output_dir)
        
    def get_searches(self):
        """Returns a LIST of searches. We don't need to nest searches here
           because Sainsbury website allows us to identify URLs directly,
           instead of having to navigate through several layers of menus."""
        if self.csv_file:
            log.msg("Spider: Fetching searches from " + self.csv_file, level=log.DEBUG)            
            return self.search_factory.get_csv_searches()            
        else:
            #Use some other source for target URLs - database?
            raise SainsburySpiderError("Cannot find input file " + self.csv_file)

    def start_requests(self):
        """Generates crawler requests for given base URL and parses results."""
        search_list = self.get_searches()
        sb_cookies = self.settings.cookies
        # Build URLs based on base URL + sub-categories
        for s in search_list:
            search_meta = {}
            product_url = ''
            search_meta = s.get_meta_map()
            search_meta['cookiejar'] = 1
            product_url = s.store_sub3
            log.msg("Spider: start_requests() yielding URL: "+product_url, level=log.DEBUG)
            yield Request(url = product_url, cookies=sb_cookies, meta=search_meta, callback=self.parse_base)                            

    def parse_base(self, response):
        """Default function to parse responses from base URL:
           Waitrose serves products in a single list, but we cannot scroll
           through them and there is no 'Next page' link, so we just extract
           the first set of up to 24 product items and yield them for processing."""
           
        # Get details of current search (passed in via response meta data)
        metadata = response.meta
        #Find product lines
        sel = Selector(response)        
        sb_cookies = self.settings.cookies
        #Find any "next" links for paging and yield Request to next page
        next_page = sel.xpath(self.settings.next_page_xpath)
        for page in next_page:
            #Check each nav link for the required sub-category
            next_link_ref = page.xpath('@href').extract()[0]
            log.msg("Spider: found NEXT page link: " + next_link_ref, level=log.DEBUG)
            yield Request(next_link_ref, cookies=sb_cookies, meta=response.meta, callback=self.parse_base)
        
        #Process each product line
        log.msg("Spider: parsing response for URL: " +
                response.url + 
                " for ONS item " + 
                metadata['ons_item_name'], level=log.DEBUG)
        products = sel.xpath(self.settings.products_xpath) 
        
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
            prodname = product.xpath(self.settings.product_name_xpath).extract()
            if len(prodname)>0:
                item['product_name'] = prodname[0].upper().strip()
                
                # WARNING:  Prices format is much more complicated on Sainsburys
                # pages, so we have to do multiple layers of extraction here to
                # get the prices while we still have access to the XPaths etc.
    
                price_block = product.xpath(self.settings.raw_price_xpath)
                raw_price_block = price_block[0]
                vol_price_block = price_block[1]
                #Extract a raw price
                ppu_price = raw_price_block.xpath('text()')[0]
                ppu_unit = raw_price_block.xpath('*/span[@class="pricePerUnitUnit"]/text()')[0]
                item['item_price_str'] = ppu_price.extract().strip() + '/' + ppu_unit.extract().strip()
                
                #Extract the components of the volume price e.g. 1.50 per 100g
                #THIS WILL BREAK IF PRICE FORMAT ON PAGE CHANGES!
                vol_abbr = vol_price_block.xpath('text()').extract()
                if vol_abbr[0].strip():
                    vol_price = vol_abbr[0].strip()
                if vol_abbr[1].strip():
                    vol_price = vol_price +' / '+ vol_abbr[1]
                else:
                    #default std quantity to 1
                    vol_price = vol_price +' / 1 '
                #Get the volume units as well    
                vol_unit = vol_price_block.xpath('*/span[@class="pricePerMeasureMeasure"]/text()')[0]    
                #Construct the vol price in known format and save it to the item
                vol_price = vol_price + vol_unit.extract().strip()       
                item['volume_price'] = vol_price
                
                # Add timestamp
                item['timestamp'] = datetime.datetime.now()
    
                #Ignore promos/offers
                item['promo'] = product.xpath(self.settings.promo_xpath).extract()
                item['offer'] = product.xpath(self.settings.offer_xpath).extract()
                
                #Pass the item back
                yield item


