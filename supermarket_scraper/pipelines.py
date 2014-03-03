# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
import datetime, re

class PostProcessingPipeline(object):
    """PostProcessingPipeline
       ======================
       Main post-processing for Tesco product items.
       Format prices, check searcht erms etc.
       """
    pound_sign = u'\xa3'

    def extract_vol_price(self,vp):
        """Convert a volume price into a dictionary:  
           e.g. 1.23/100g --> {'units': 'g', 'price': 1.23, 'no_units': '100'}
           Any errors --> return dict with values = ''.
           """
        try:
            vp_elems = re.split('/',vp)
            # convert e.g. 1,234.00 to 1234.00
            p_str     = re.sub(r'\[^0-9.]|,', "", (vp_elems[0].strip(self.pound_sign)))
            # now make it a number
            price = 1.0 * float(p_str)
            no_units = re.sub(r'\D', "", vp_elems[1])
            if not no_units:
                no_units = 1.0
            units = re.sub(r'\d', "", vp_elems[1])
            return {'price':price,'no_units':no_units,'units':units}
        except:
            return {'price':'','no_units':'','units':''}

    def get_search_matches(self, search_terms, item_desc):
        """Count how many search terms match the given description and
           return a metric e.g. 1.0 for full match, 0.5 for 1 out of 2, etc.
           Returns 1.0 if no search terms provided."""
        if not search_terms:
            return 1.0
        else:
            terms = search_terms.split(" ")
            n_terms = len(terms)
            if n_terms == 0:
                return 1.0
            else:
                desc = item_desc.split()
                # If no search terms, let matches = 1.0
                n_matches = 0.0
                for term in terms:
                    t = term.strip().upper()
                    if t in desc:
                        n_matches += 1.0
                return round(n_matches/n_terms,2)

    def extract_std_price(self, unit_price, no_units, unit):
        """Convert unit price to a standardised price per kg, litre or each"""
        std_price = 0.0
        std_unit = 'unknown'
        if unit == 'g':
            #Convert to price per kg
            std_unit = 'kg'
            std_price = float(unit_price) * 1000.0 / float(no_units)
        elif unit == 'ml':
            std_unit = 'l'
            std_price = float(unit_price) * 1000.0 / float(no_units)
        elif unit == 'cl':
            std_unit = 'l'
            std_price = float(unit_price) * 100.0 / float(no_units)
        elif unit in ['kg','l','each']:
            std_unit = unit
            std_price = unit_price    
        
        return (round(std_price,2), std_unit)

    def process_tesco_item(self, item, spider):
        """Apply Tesco-specific post-processing to product line items"""
        #Remove pound sign from price entry for Tesco and convert to float
        if item['item_price_str']:
            item['item_price_num'] = 1.0 * float(item['item_price_str'].strip(self.pound_sign) )

        #Strip blanks from around volume price
        item['volume_price'] = (item['volume_price']).strip(' ()')
        #Extract voume price
        if item['volume_price']:            
            vpx = self.extract_vol_price(item['volume_price'])
            item['unit_price'] = vpx.get('price')
            item['no_units'] = vpx.get('no_units')
            item['units'] = vpx.get('units')
            # Work out the standardised price per kg or litre 
            (item['std_price'], item['std_unit']) = self.extract_std_price(vpx.get('price'), vpx.get('no_units'), vpx.get('units'))
        #Check how many search terms match the product name
        item['search_matches'] = self.get_search_matches(item['search_string'],  item['product_name'])
            
        return item
    
    def process_item(self, item, spider):
        """Apply post-processing to product line items"""
        if spider.name == 'tesco':
            #Apply specific processing for Tesco
            return self.process_tesco_item(item, spider)
        else:
            #Return item unchanged for processing elsewehre
            return item
            

class CsvExportPipeline(object):
    """CsvExportPipeline
       =================
       TescoSpider includes output_dir attribute provided at runtime.
       We specify the fields_to_export in the CsvItemExporter to make sure the 
       fields are written to the CSV file in the correct order.
    """
    def __init__(self):
        #super(CsvExportPipeline, self).__init__()  
        self.files = {}
        self.fields_to_export = ['timestamp','store',
        'ons_item_no','ons_item_name','product_type',
        'search_string','search_matches','product_name',
        'item_price_str','item_price_num',
        'volume_price','unit_price','no_units','units','std_price','std_unit',
        'promo','offer']          

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
        self.exporter.export_item(item)
        return item

        