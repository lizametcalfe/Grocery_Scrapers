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
    cookies = {}

class WaitroseSearchSettings(SearchSettings):
    """Represents search paths for WAITROSE.
       May want to load these at runtime from a CSV file."""
    
    def __init__(self):
        super(WaitroseSearchSettings, self).__init__()
        self.base_url = 'http://www.waitrose.com/shop/Browse/Groceries'
        # Waitrose website uses REST-like URLs so we do not need to hunt for
        # navigation links for sub-categories via sub1_path etc.        

        # Exclude offer block above main product listings
        self.products_xpath = '//*/div[@class="products-row"]/*[not(contains(@id,"caro-"))]/div[contains(@class,"m-product-cell")]/div[contains(@class,"m-product ")]'
        self.product_name_xpath = '*/div[@class="m-product-details-container"]/*/a/text()'         
        self.raw_price_xpath = '*/div[@class="m-product-price-container"]/span[@class="price"]/text()'
        self.volume_xpath = '*/div/div/div[@class="m-product-volume"]/text()'
        self.vol_price_xpath = '*/div[@class="m-product-price-container"]/span[@class="fine-print"]/text()'        

        self.promo_xpath = '*/div[@class="m-product-details-container"]/a/text()'
        self.offer_xpath = '*/div[@class="m-product-details-container"]/a/text()'        


class TescoSearchSettings(SearchSettings):
    """Represents search paths for TESCO.
       May want to load these at runtime from a CSV file."""
    
    def __init__(self):
        super(TescoSearchSettings, self).__init__()
        self.base_url = 'http://www.tesco.com/groceries'
        self.sub1_path = '//*[@id="secondaryNav"]/ul/li/a[@class="yui3-menu-label level2"]'
        self.sub2_path = '//*[@id="superDeptItems"]/*/ul/li/a'
        self.sub3_path = '//*[@id="deptNavItems"]/*/ul/li/a'
        self.next_page_xpath = "//*[@class='next']/a"
        
        #working 
        self.products_xpath = "//*/li[contains(@class,'product clearfix')]"
        #working 
        self.product_name_xpath = "*[@class='desc']/h2/a/span[@data-title='true']/text()"
        #working
        self.raw_price_xpath = "*[@class='quantityWrapper']/div/p/span[@class='linePrice']/text()"
        #working
        self.vol_price_xpath = "*[@class='quantityWrapper']/div/p/span[@class='linePriceAbbr']/text()"
        self.promo_xpath = "*[@class='desc']/*[@class='descContentGrid']/*[@class='promo']/a[contains(@class,'promotionAlternatives')]/@title"
        self.offer_xpath = "*[@class='desc']/*[@class='descContentGrid']/*[@class='promo']/a[contains(@class,'promotionAlternatives')]/em/text()"
  
class SainsburySearchSettings(SearchSettings):
    """Represents search paths for SAINSBURY.
       May want to load these at runtime from a CSV file.
       WARNING:
       Sainsburys page format is a world of pain, and we have had to put some
       XPath in the spider class to cope with this.
       Be VERY careful about changing ANY of this stuff."""
    
    def __init__(self):
        super(SainsburySearchSettings, self).__init__()
        self.base_url = 'http://www.sainsburys.co.uk/shop/gb/groceries/'        
        self.products_xpath = "//*/li[contains(@class,'gridItem')]/div[contains(@class,'product ')]"        
        self.product_name_xpath = "*[@class='productInfo']/*/h3/a/text()" 
        
        self.next_page_xpath = "//*[@id='productLister']/div[@class='pagination']/ul[@class='pages']/li[@class='next']/a"
        #this is not working 
        self.raw_price_xpath = "..//*[@class='pricing']/p"
        # "*[@id='productLister']/ul/li/div/div[3]/div[1]/div[1]/div[1]/div[1]/p[1]"
        #"*[@class='pricing']/*/[@class='pricePerUnit']"
        #"//*[@class='pricePerUnit']" #//text()"
        #"*[@class='pricingReviews']/*/p" #//text()

        # sort of working 
        #"//*[@class='pricePerUnit']"
        # rb test "//*[@class='pricing']/p/text()"
        # this is not working
        self.vol_price_xpath = "..//*[@class='pricing']/p[2]/text()"
        self.vol_unit = "..//*[@class='pricing']/p[2]/abbr[2]/span/text()"
        # unit measure "//*[@class='pricePerMeasureMeasure']/text()"
        #"*[@class='quantity']/div/p/span[@class='linePriceAbbr']/text()"
        self.promo_xpath = "*[@class='productInfo']/*/div[@class='promotion']/p/a/text()"
        self.offer_xpath = "*[@class='productInfo']/*/div[@class='promotion']/p/a/text()"
        # Sainsburys requires us to accept cookies before we can navigate the store
        '''self.promo_xpath = "*[@class='desc']/*[@class='descContent']/*[@class='promo']/a[contains(@class,'promoFlyout')]/@title"
        self.offer_xpath = "*[@class='desc']/p[@class='limitedLife']/a/text()" 
        "*[@class='pricingReviews']/*/p"
        rb latest 
        "//*[@class='productInfo']/*/div[@class='promotion']/p/a/text()"
        '''
        self.cookies = {}
        self.cookies['SESSION_COOKIEACCEPT']='true'
        
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
        elif store == "SAINSBURY":            
            return SainsburySearchSettings()
        else:
            # Fail safe by returning empty settings
            return SearchSettings()
