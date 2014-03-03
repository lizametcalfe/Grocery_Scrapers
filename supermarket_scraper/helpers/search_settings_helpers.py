# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 11:51:02 2014

@author: onsbigdata
"""

class SearchSettings(object):
    """Represents search paths for a given store."""
    base_url = ''
    sub1_xpath = ''
    sub2_xpath = ''
    sub3_xpath = ''
    next_page_xpath= ''
    products_xpath= ''
    product_name_xpath = ''
    raw_price_xpath = ''
    vol_price_xpath = ''
    




class AsdaSearchSettings(SearchSettings):
    """Represents search paths for TESCO.
       May want to load these at runtime from a CSV file."""
    
    def __init__(self):
        super(TescoSearchSettings, self).__init__()
        self.base_url = 'http://groceries.asda.com/asda-webstore/landing/home.shtml'
        
        self.sub1_xpath = '//*[@id="primary-nav-wrapper"]/ul/div[@class="primary-nav-items"/li/a'
        
        self.sub2_xpath = '//*[@id="superDeptItems"]/*/ul/li/a'
        self.sub3_xpath = '//*[@id="deptNavItems"]/*/ul/li/a'
        self.next_page_xpath = "//*[@class='next']/a"
        self.products_xpath = "//*[@class='cf products line']/li"
        self.product_name_xpath = "*[@class='desc']/*/a[contains(@class,'title')]/text()" 
        self.raw_price_xpath = "*[@class='quantity']/div/p/span[@class='linePrice']/text()"
        self.vol_price_xpath = "*[@class='quantity']/div/p/span[@class='linePriceAbbr']/text()"
        self.promo_xpath = "*[@class='desc']/*[@class='descContent']/*[@class='promo']/a[contains(@class,'promoFlyout')]/@title"
        self.offer_xpath = "*[@class='desc']/p[@class='limitedLife']/a/text()" 


class TescoSearchSettings(SearchSettings):
    """Represents search paths for TESCO.
       May want to load these at runtime from a CSV file."""
    
    def __init__(self):
        super(TescoSearchSettings, self).__init__()
        self.base_url = 'http://www.tesco.com/groceries'
        self.sub1_xpath = '//*[@id="secondaryNav"]/ul/li/a[@class="flyout"]'
        self.sub2_xpath = '//*[@id="superDeptItems"]/*/ul/li/a'
        self.sub3_xpath = '//*[@id="deptNavItems"]/*/ul/li/a'
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
        else:
            # Fail safe by returning empty settings
            return SearchSettings()
