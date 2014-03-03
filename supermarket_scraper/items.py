# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ProductItem(Item):
    """Price item for Tesco."""
    store = Field()
    ons_item_no = Field()
    ons_item_name = Field()
    product_type = Field()
    product_name = Field()
    promo = Field()
    offer = Field()
    item_price_str = Field()
    volume_price = Field()
    search_string = Field()
    units = Field()    
    std_unit = Field()    
    # Need to supply a serializer for non-string fields
    search_matches = Field(serializer=str)
    item_price_num = Field(serializer=str)
    unit_price = Field(serializer=str)
    std_price = Field(serializer=str)
    no_units = Field(serializer=str)
    timestamp = Field(serializer=str)
