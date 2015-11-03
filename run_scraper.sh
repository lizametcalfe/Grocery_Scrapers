#!/bin/bash          

echo "$(date) Started Running Scrapy to crawl Tesco Web Site"

scrapy crawl tesco 

echo "$(date) Finished Running Scrapy to crawl Tesco Web Site"

echo "$(date) Started Running Scrapy to crawl waitrose Web Site"

scrapy crawl waitrose 

echo "$(date) Finished Running Scrapy to crawl waitrose Web Site"

echo "$(date) Started Running Scrapy to crawl sainsbury Web Site"

scrapy crawl sainsbury

echo "$(date) Finished Running Scrapy to crawl sainsbury Web Site"