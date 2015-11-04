#!/bin/bash          

echo "$(date) Started Running Scrapy to crawl Tesco Web Site"

scrapy crawl tesco 

echo "$(date) Finished Running Scrapy to crawl Tesco Web Site"
