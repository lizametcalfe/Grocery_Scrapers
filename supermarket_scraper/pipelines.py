# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# incorporating a machine learning pipeline 

from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
import datetime, re
import pickle
import pandas as pd 
import search_loader 

class PostProcessingPipeline(object):
    """PostProcessingPipeline
       ======================
       Main post-processing for supermarket product items.
       Format prices, check search terms etc.
       """
       
    # UTF makes pound sign behave weirdly, so use this literal value   
    pound_sign1 = u'\xa3'
    pound_sign2 = u'\xc2'

    def extract_multipack_volume(self, vp_in):
        """Convert vp_in from multipack volume e.g. 10x440ml to e.g. 4400 ml"""
        # Watch out for multi-pack volumes e.g. 10x440ml
        re_find_vol = r'\d+(x)\d+'   # RE looks for e.g. "10x440" 
        re_vol = re.match(re_find_vol,vp_in)
        if re_vol:    
            #Re-format multipack volume e.g. 10x440 --> [10 440] --> 4400
            vs = re_vol.group().split('x')
            tmp_vol = str(float(vs[0]) * float(vs[1]))
            # Get units as well (by dropping numbers)
            tmp_units = re.sub(re_find_vol, "", vp_in)
            # Re-build vol using these values e.g. '4400 ml'
            return (tmp_vol + ' ' + tmp_units)
        else:
            return vp_in

    def extract_vol_price(self,vp):
        """Convert a volume price into a dictionary:  
           e.g. 1.23/100g --> {'units': 'g', 'price': 1.23, 'no_units': '100'}
           Any errors --> return dict with values = ''.
           """
        try:
            #First break up the vol price string into individual elements
            vp_in = vp.strip(" ()").replace("each","/each")
            vp_elems = re.split('/', vp_in)
            # convert e.g. 1,234.00 to 1234.00
            p_str     = re.sub(r'\[^0-9.]|,', "", 
                               (vp_elems[0].strip(' '+self.pound_sign1)))
            # now make it a number - watch out for penny prices e.g. "89p"
            if 'p' in p_str:
                # penny price --> pounds
                price = float(p_str.replace('p',''))/100.0
            else:
                price = 1.0 * float(p_str.strip(' '+self.pound_sign1) )
        
            # Now look for no of units
            vol = vp_elems[1].strip()
            # Watch out for multi-pack volumes e.g. 10x440ml --> 4400 ml
            vol = self.extract_multipack_volume(vol)                
            # Extract no of units using regex
            re_find_price = r'\d+(\.)?\d*'    
            re_price = re.match(re_find_price, vol)
            if re_price:
                #Get the number of units
                no_units = re_price.group()
            else:
                no_units = 1.0
            # Now find actual units e.g. "kg" by removing number of units  
            units = (re.sub(re_find_price, "", vol)).strip(' ()')
            #If no units found, assume "each"
            if not units:
                units = 'each'
    
            return {'price':price,'no_units':no_units,'units':units}        
            
        except:
            #Just return dictionary for now
            return {'price':'','no_units':'','units':''}

    def extract_std_price(self, unit_price, no_units, unit):
        """Convert unit price to a standardised price per kg, litre or each"""
        std_price = 0.0
        std_unit = 'unknown'
        if unit.strip() == 'g':
            #Convert to price per kg
            std_unit = 'kg'
            std_price = float(unit_price) * 1000.0 / float(no_units)
        elif unit.strip() == 'ml':
            std_unit = 'l'
            std_price = float(unit_price) * 1000.0 / float(no_units)
        elif unit.strip() == 'cl':
            std_unit = 'l'
            std_price = float(unit_price) * 100.0 / float(no_units)
        elif unit.strip() == 'litre':
            std_unit = 'l'
            std_price = float(unit_price) / float(no_units)   
        elif unit.strip() == 'ltr':
            std_unit = 'l'
            std_price = float(unit_price) / float(no_units)   
        elif unit.strip() in ['kg','l','each']:
            std_unit = unit
            std_price = float(unit_price) / float(no_units)   
        elif unit =='ea':
            std_unit = 'each'
            std_price = float(unit_price) / float(no_units)   
        elif unit =='':
            std_unit = 'each'
            std_price = float(unit_price) / float(no_units)   
        
        return (round(std_price,4), std_unit)

    def get_search_matches(self, search_terms, item_desc):
        """Count how many search terms match the given description and
           return a metric e.g. 1.0 for full match, 0.5 for 1 out of 2, etc.
           Returns 1.0 if no search terms provided."""
        if (not search_terms) or (not search_terms.strip()):
            return 1.0
        else:
            # Excludes blank search terms
            terms = [t.strip() for t in search_terms.split(' ') if t.strip()]
            n_terms = len(terms)
            if n_terms == 0:
                return 1.0
            else:
                # split description on '-' or blank:
                desc = item_desc.replace('-',' ').split()
                # If no search terms, let matches = 1.0
                n_matches = 0.0
                for term in terms:
                    t = term.strip().upper()
                    if t in desc:
                        n_matches += 1.0
                return round(n_matches/n_terms,2)

    #
    # STORE-SPECIFIC PIPELINE PROCESSING
    #

    def common_process_item(self, item, spider):
        """Apply any common post-processing to product line items"""
        #Machine learning flag across items 
        if item['product_name']:
        	#pre estimated SVM machine learning classifier 
        	#item_model_dump = "/home/mint/my-data/testing/supermarket_scraper/supermarket_scraper/ml_model/apple cider, bottle, 4.5%-5.5% abv_dump_model1"
        	#pkl_file = open(item_model_dump, 'rb')
        	try:
        		pkl_file = search_loader.SearchLoader().generic_opener(item['ons_item_name'].lower())
        		stored_model = pickle.load(pkl_file)
        		pkl_file.close()
        		#pre processing of product name 
        		item['product_name'] = item['product_name'].lower()
        		#applying the machine SVM classifier (item by item)
        		item['ml_prediction'] = stored_model.predict([item['product_name']])[0]
        		item['single_class'] = 0

        	except:
        		item['ml_prediction'] = 1
        		item['single_class'] = 1 
		    #Check how many search terms match the product name
			#item['search_matches'] = self.get_search_matches(item['search_string'], item['product_name'])

		#standard processing: Remove pound sign from price entry and convert to float

        if item['item_price_str']:
            # Allow for e.g. "85p":
            if 'p' in item['item_price_str']:
                item['item_price_num'] = float(item['item_price_str'].strip().replace('p',''))/100.0
            else:
                item['item_price_num'] = 1.0 * float(item['item_price_str'].strip(' '+self.pound_sign1) )

        #Extract volume price
        if item['volume_price']:            
            vpx = self.extract_vol_price(item['volume_price'].lower())
            item['unit_price'] = vpx.get('price')
            item['no_units'] = vpx.get('no_units')
            item['units'] = vpx.get('units')
            # Now work out the standardised price per kg or litre or each
            (item['std_price'], item['std_unit']) = self.extract_std_price(
                                                    vpx.get('price'), 
                                                    vpx.get('no_units'), 
                                                    vpx.get('units'))
        
                                    

        return item


    def process_tesco_item(self, item, spider):
        """Apply Tesco-specific post-processing (if any) to product line items"""        
        # Currently we can use common processing for both supermarkets
        return self.common_process_item(item, spider)

    def process_waitrose_item(self, item, spider):
        """Apply Waitrose-specific post-processing to product line items"""        
        # Currently we can use common processing for both supermarkets
        return self.common_process_item(item, spider)


    def process_sainsbury_item(self, item, spider): 
    	if item['product_name']:
    		#pre estimated SVM machine learning classifier 
    		#item_model_dump = "/home/mint/my-data/testing/supermarket_scraper/supermarket_scraper/ml_model/apple cider, bottle, 4.5%-5.5% abv_dump_model1"
    		#pkl_file = open(item_model_dump, 'rb')
    		try:
    			pkl_file = search_loader.SearchLoader().generic_opener(item['ons_item_name'].lower())
    			stored_model = pickle.load(pkl_file)
    			pkl_file.close()
    			#pre processing of product name 
    			item['product_name'] = item['product_name'].lower()
    			#applying the machine SVM classifier (item by item)
    			item['ml_prediction'] = stored_model.predict([item['product_name']])[0]
    			item['single_class'] = 0
    			#Check how many search terms match the product name
    	
    		except:
    			item['ml_prediction'] = 1
    			item['single_class'] = 1 
			
				#item['search_matches'] = self.get_search_matches(
			                            #item['search_string'],  
			                            #item['product_name'])

        #Remove pound sign from price entry and convert to float
        if item['item_price_str']:
            # Allow for e.g. "85p":
            price = item['item_price_str'].strip().split('/')[0]
            if 'p' in price:
                item['item_price_num'] = float(price.strip().replace('p',''))/100.0
            else:
                item['item_price_num'] = 1.0 * float(price.strip(' '+self.pound_sign1) )

        #Extract volume price
        if item['volume_price']:            
            vpx = self.extract_vol_price(item['volume_price'].lower())
            item['unit_price'] = vpx.get('price')
            item['no_units'] = vpx.get('no_units')
            item['units'] = vpx.get('units')
            # Now work out the standardised price per kg or litre or each
            (item['std_price'], item['std_unit']) = self.extract_std_price(
                                                    vpx.get('price'), 
                                                    vpx.get('no_units'), 
                                                    vpx.get('units'))
        return item

    #
    # MAIN STORE ITEM PROCESSOR
    #
    
    def process_item(self, item, spider):
        """Apply post-processing to product line items.
           Must return an Item for subsequent processing."""
        if spider.name == 'tesco':
            #Apply specific processing for Tesco
            return self.process_tesco_item(item, spider)
        elif spider.name == 'waitrose':
            #Apply specific processing for Waitrose
            return self.process_waitrose_item(item, spider)
        elif spider.name == 'sainsbury':
            #Apply specific processing for Sainsbury
            return self.process_sainsbury_item(item, spider)
        else:
            #Return item unchanged for processing elsewhere
            return item

#
# CSV PIPELINE
#            

class CsvExportPipeline(object):
    """CsvExportPipeline
       =================
       Spider includes output_dir attribute provided at runtime.
       We specify the fields_to_export in the CsvItemExporter to make sure the 
       fields are written to the CSV file in the correct order.
       Must return an Item for subsequent processing.
    """
    def __init__(self):
        #super(CsvExportPipeline, self).__init__()  
        self.files = {}
        self.fields_to_export = ['timestamp','store',
        'ons_item_no','ons_item_name','product_type',
        'search_string','product_name',
        'item_price_str','item_price_num',
        'volume_price','unit_price','no_units','units','std_price','std_unit',
        'promo','offer','ml_prediction','single_class']          

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def get_file_name(self, spider, ext):
        """
        spider:  includes output directory name.
        ext: file extension e.g. 'csv'
        
        Generates a file name with a timestamp YYYYMMDDHHMMSS like:
        tesco_products_20140302114309.csv
        """
        timestamp = datetime.datetime.now()
        fname = spider.name + "_products_" + timestamp.strftime("%Y%m%d%H%M%S") + "." + ext
        return spider.output_dir + "/" + fname
        
    def spider_opened(self, spider):
        fname = self.get_file_name(spider,"csv")
        file = open(fname, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file, fields_to_export=self.fields_to_export)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        """Export item to CSV.
           Must also return item for subsequent processing."""
        self.exporter.export_item(item)
        return item

        