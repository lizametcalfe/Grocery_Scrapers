# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:15:41 2014

@author: onsbigdata
"""

# Standard Python classes
import datetime
import os
import sys
## selenium
from selenium import webdriver
import time
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException	
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from pyvirtualdisplay import Display

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
        ## selenium
	self.display = Display(visible=0, size=(1920, 1080))
	self.display.start()
	self.driver = webdriver.Firefox()
	self.driver.wait = WebDriverWait(self.driver, 5)
	#self.driver.maximize_window()
	self.driver.set_window_size(1920, 1080)
	time.sleep(20)
	self.tb = 'tb none'
	dispatcher.connect(self.spider_closed, signals.spider_closed)
	#i=0
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
       
        sb_cookies = self.settings.cookies
        product_url = "http://www.sainsburys.co.uk"
        log.msg("Spider: start_requests() yielding URL: "+product_url, level=log.DEBUG)
        yield Request(url = product_url, cookies=sb_cookies,callback=self.parse_base)                            

    def parse_base(self, response):
        
        """Default function to parse responses from base URL:
           Waitrose serves products in a single list, but we cannot scroll
           thro ugh them and there is no 'Next page' link, so we just extract
           the first set of up to 24 product items and yield them for processing."""
      	search_list = self.get_searches()
     	for s in search_list:
		search_meta = {}
		product_url = ''
		search_meta = s.get_meta_map()
		product_url = s.store_sub3
	
		
		
		self.driver.get(product_url)
		sel = Selector(text=self.driver.page_source) 
		first_page_parse_finished = None
		log.msg("Spider: start_requests() yielding URL:"+product_url, level=log.DEBUG)
		while True:
	    		try:
				
				if first_page_parse_finished:
					#Find any "next" links for paging 
            				next_element = self.driver.find_element_by_xpath(self.settings.next_page_xpath)
					debug_text_class = next_element.get_attribute('href')
					button = self.driver.wait.until(EC.element_to_be_clickable((By.XPATH,self.settings.next_page_xpath)))
                			button.click()
					time.sleep(3)

				first_page_parse_finished = True
				sel = Selector(text=self.driver.page_source) 
        			products = sel.xpath(self.settings.products_xpath)
        			for product in products:
            				# Create an item for each entry
            				item = ProductItem()
            				item['store'] = self.store
					#print('store field of item object', item['store'])
            				item['ons_item_no'] =  search_meta['ons_item_no']
            				item['ons_item_name'] =  search_meta['ons_item_name']
            				item['product_type'] =  search_meta['store_sub3']
            				item['search_string'] = search_meta['search_terms']

            				#Default matches to 1.0 and modify later            
            				#item['search_matches'] = 1.0
            				#UPPER case product name for storage to make searching easier
           				prodname = product.xpath(self.settings.product_name_xpath).extract()
            				if len(prodname)>0:
                				item['product_name'] = prodname[0].upper().strip()
						#print 'SPIDER :: sainsbury :: product_name',format(item['product_name'].encode('utf-8'))
                				# WARNING:  Prices format is much more complicated on Sainsburys
                				# pages, so we have to do multiple layers of extraction here to
                				# get the prices while we still have access to the XPaths etc.
    
                				price_block = product.xpath(self.settings.raw_price_xpath)
                				raw_price_block = price_block[0]
                				vol_price_block = price_block[1]
                				#price_block[0]
                				#price_block[1]
                				#print('individual item prices ', raw_price_block)
                				#print('individual volume item prices ', vol_price_block)
                				#Extract a raw price
                				ppu_price = raw_price_block.xpath('text()')[0]
                				ppu_unit = raw_price_block.xpath('*/span[@class="pricePerUnitUnit"]/text()')[0]
                				item['item_price_str'] = ppu_price.extract().strip() + '/' + ppu_unit.extract().strip()
                				#print('individual item prices processed', item['item_price_str'])
                				#Extract the components of the volume price e.g. 1.50 per 100g
                				#THIS WILL BREAK IF PRICE FORMAT ON PAGE CHANGES!
                				vol_abbr = vol_price_block.xpath('text()').extract()
                				#print('volume_unit_raw', vol_abbr )
                				if vol_abbr[0].strip():
                    					vol_price = vol_abbr[0].strip()
                				if vol_abbr[1].strip():
                    					vol_price = vol_price +' / '+ vol_abbr[1]
               					else:
                    				#default std quantity to 1
                    		 			vol_price = vol_price +' / 1 '
                				#Get the volume units as well    

                				#exception added as the last two unit_vol's were not collecting, this adds an NA in when this is the case and parses to the next product
                				try:
                    					vol_unit = product.xpath(self.settings.vol_unit)[2]
                    					vol_price = vol_price + vol_unit.extract().strip()
               					except:
                    					#default std quantity to 1
                    					vol_unit = "NA"
                    					vol_price = vol_price + vol_unit
                				#Get the volume units as well    
               					#print('vol_unit', vol_unit)
                				#print('vol _nunit', vol_unit)
                				#vol_price_block.xpath("*/span[@class='pricePerMeasureMeasure']/text()")  
                				#Construct the vol price in known format and save it to the item
                				item['volume_price'] = vol_price
                				#print('vol _nunit',  item['volume_price'])
                				# Add timestamp
                				item['timestamp'] = datetime.datetime.now()
    
                				#Ignore promos/offers
                				item['promo'] = product.xpath(self.settings.promo_xpath).extract()
                				item['offer'] = product.xpath(self.settings.offer_xpath).extract()
                
                				#Pass the item back
            	    				yield item
			except NoSuchElementException:
				#print 'Inside NoSuchElementException handling::: '
				break
			except:
				self.tb = traceback.format_exc()
				log.msg("Spider: parse request :Inside Exception handling:::"+self.tb , level=log.DEBUG)
				#print 'Inside Exception handling::: ',self.tb
				break

    def spider_closed(self, spider):
	#print "--- %s seconds ---" % (time.time() - start_time))
	self.display.stop()
        self.driver.quit()


