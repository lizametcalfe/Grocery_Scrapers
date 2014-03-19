# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 11:51:02 2014

@author: onsbigdata
"""

class SearchSettings(object):
    """Represents search paths for a given store."""
    base_url = ''
    sub1_path = ''
    sub2_path = ''
    sub3_path = ''
    next_page_xpath= ''
    products_xpath= ''
    product_name_xpath = ''
    raw_price_xpath = ''
    vol_price_xpath = ''    
    volume_xpath = ''    

class WaitroseSearchSettings(SearchSettings):
    """Represents search paths for WAITROSE.
       May want to load these at runtime from a CSV file."""
    
    def __init__(self):
        super(WaitroseSearchSettings, self).__init__()
        self.base_url = 'http://www.waitrose.com/shop/Browse/Groceries'
        # Waitrose website uses REST-like URLs so we do not need to hunt for
        # navigation links for sub-categories.        
        self.sub1_path = ''        
        self.sub2_path = ''
        self.sub3_path = ''
        self.next_page_xpath = ''

        # Exclude offer block above main product listings
        self.products_xpath = '//*/div[@class="products-row"]/*[not(contains(@id,"caro-"))]/div[contains(@class,"m-product-cell")]/div[contains(@class,"m-product ")]'
        self.product_name_xpath = '*/div[@class="m-product-details-container"]/*/a/text()'         
        self.raw_price_xpath = '*/div[@class="m-product-price-container"]/span[@class="price"]/text()'
        self.volume_xpath = '*/div/div/div[@class="m-product-volume"]/text()'
        self.vol_price_xpath = '*/div[@class="m-product-price-container"]/span[@class="fine-print"]/text()'        
        self.promo_xpath = ''
        self.offer_xpath = ''        


class TescoSearchSettings(SearchSettings):
    """Represents search paths for TESCO.
       May want to load these at runtime from a CSV file."""
    
    def __init__(self):
        super(TescoSearchSettings, self).__init__()
        self.base_url = 'http://www.tesco.com/groceries'
        self.sub1_path = '//*[@id="secondaryNav"]/ul/li/a[@class="flyout"]'
        self.sub2_path = '//*[@id="superDeptItems"]/*/ul/li/a'
        self.sub3_path = '//*[@id="deptNavItems"]/*/ul/li/a'
        self.next_page_xpath = "//*[@class='next']/a"
        self.products_xpath = "//*[@class='cf products line']/li"
        self.product_name_xpath = "*[@class='desc']/*/a[contains(@class,'title')]/text()" 
        self.raw_price_xpath = "*[@class='quantity']/div/p/span[@class='linePrice']/text()"
        self.vol_price_xpath = "*[@class='quantity']/div/p/span[@class='linePriceAbbr']/text()"
        self.promo_xpath = "*[@class='desc']/*[@class='descContent']/*[@class='promo']/a[contains(@class,'promoFlyout')]/@title"
        self.offer_xpath = "*[@class='desc']/p[@class='limitedLife']/a/text()" 
            
        
class SearchSettingsFactory(object):
    """Returns path settings (URLs etc) for product searches at a given store.
       Has no internal state so no need to instantiate."""
                    
    @classmethod
    def get_settings(cls, store):
        """cls = class (required but not specified in calls).
           store = name of store e.g. TESCO."""
        if store == "TESCO":            
            return TescoSearchSettings()
        elif store == "WAITROSE":            
            return WaitroseSearchSettings()
        else:
            # Fail safe by returning empty settings
            return SearchSettings()
