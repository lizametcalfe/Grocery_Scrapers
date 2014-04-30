# -*- coding: utf-8 -*-
# Scrapy settings for scrapy_tesco project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import datetime

COOKIES_ENABLED=True
COOKIES_DEBUG=True
BOT_NAME = 'supermarket_scraper'
SPIDER_MODULES = ['supermarket_scraper.spiders']
NEWSPIDER_MODULE = 'supermarket_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'ons_supermarket_scraper (+http://www.ons.gov.uk)'

# OUR CUSTOM SETTINGS:

LOG_LEVEL = 'ERROR'  # use 'ERROR' to suppress non-error log messages
# Use this option if you want to include the timestamp in the log file name
#logfile = BOT_NAME + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
logfile = BOT_NAME + ".log"
LOG_FILE = logfile

# Switch off DNS caching because we get mixed up request/response data.
# May not be relevant to the problem, but seems to work OK if set to False.
DNSCACHE_ENABLED = False

# Try increasing CONCURRENT_REQUESTS to handle all requests concurrently, 
# as this seems to help prevent the request/response mix-ups.
# Might hit memory problems here?
CONCURRENT_REQUESTS = 100

# PIPELINES
# =========
# Pipelines are used for extra processing of each item after scraping.
#
# * PostProcessingPipeline cleans up price entry. ALWAYS RUN THIS.
#
# * Use MongoDB pipeline to write results straight to MongoDB database
#   (requires scrapy-mongodb https://github.com/sebdah/scrapy-mongodb).
#   Uncomment the line for scrapy_mongodb.MongoDBPipeline in ITEM_PIPELINES
#   below and also confirm the DB settings below if you want to do this.
#
# * CsvExportPipeline writes data to a CSV file in the output directory.
#
#   CSV file names include a timestamp.  For example:
#     tesco_products_2014-02-17T10:13:48.675375.csv
#
# ITEM_PIPELINES:
# Number in each entry indicates order to execute pipelines.
# You can run all of the pipelines if you want multiple output formats.

ITEM_PIPELINES = {
    'supermarket_scraper.pipelines.PostProcessingPipeline': 300,
    'supermarket_scraper.pipelines.CsvExportPipeline': 400,
#    'scrapy_mongodb.MongoDBPipeline': 800,
}

# MongoDB database settings for scrapy_mongodb.MongoDBPipeline
# (can put user/pwd in DB URL e.g. 'mongodb://ons:ons123@localhost:27017'):
MONGODB_URI = 'mongodb://localhost:27017'  
MONGODB_DATABASE = 'scrapy'
MONGODB_COLLECTION = 'item_prices'
# This would add a timestamp as a nested field {scrapy-mongodb:{ts:...}}
# MONGODB_ADD_TIMESTAMP = True

