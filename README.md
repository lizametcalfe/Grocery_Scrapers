ONS Big Data: Web scraping prices
=================================

Prototype: Tesco
----------------

Initial prototype for web-scraping price information from public websites.  Installation tips below assume you are working on a Ubuntu/Debian-based Linux system e.g. Ubuntu, Linux Mint etc.  You may also be prompted to download dependencies in some cases.

### Software
The following are needed to run the basic web-scraping process (on Linux):

* Linux Mint
* Python 2.7 (should already be installed on any modern Linux system)
* Python PIP package installer e.g. on Ubuntu/Debian run:  `sudo apt-get install python-pip`
* Scrapy web-scraping framework e.g. `pip install Scrapy`
* Nose - testing framework for Python e.g. `pip install nose`

The following tools are optional, depending on whether you want to store your data in MongoDB, use Git version control, etc.

* MongoDB database e.g. `sudo apt-get install mongodb`
* PyMongo database driver e.g. `pip install pymongo`
* scrapy-mongodb add-on to write Scrapy output straight to MongoDB e.g. `pip install scrapy-mongodb`
* Robomongo GUI client for MongoDB.  Download .DEB package and install using package manager.
* Git source code management (remote repository: BitBucket) e.g. `sudo apt-get install git`
* SmartGit GUI client for Git.  Download .DEB package and install using package manager.
* Gedit text-editor with Markdown plugin e.g. `sudo apt-get install gedit`

### Running Scrapy with our Tesco spider
* The list of products to scrape is held in a CSV file:
>>>`scrapy_tesco/scrapy_tesco/data/tesco.csv`
* You tell Scrapy the name of this input file at runtime:
>>>`scrapy crawl tesco -a csv_file=tesco.csv`
* This file should exist in the data directory: `scrapy_tesco/scrapy_tesco/data`
* If the filename is not provided at runtime, the program looks for a default file `tesco.csv`.
* **Warning:** there have been some problems with character-sets if this file is generated from Excel or OpenOffice: **use a plain text editor instead!**

* We have various "pipelines" that allow you to write the scraped items to various outputs.
* You can provide a relative path to the output directory at runtime:
>>>`scrapy crawl tesco -a csv_file=tesco.csv -a output_dir=output`
* This will write any output files to this directory (this is also the default value):
>>>`scrapy_tesco/output`
* The output formats are specified via the "pipeline" settings in `settings.py` (see "Outputs" below).

Outputs - see `scrapy_tesco/settings.py`
--------------------------------------
* Scrapy allows us to define ITEM_PIPELINES to send the items down a "pipe" for further processing.
* We have implemented several pipelines:
> * Price pipeline cleans up price entry (Tesco). **ALWAYS RUN THIS**.
> * MongoDB pipeline writes item to MongoDB database if required.
> * CSV pipeline writes data to a CSV file in the output directory.
* CSV file names include a timestamp.  For example:
> `tesco_products_20140302132432.csv`

DEVELOPMENT
----------
### Functionality
* Build a working skeleton to scrape data for a number of products from Tesco website.
* No validation on data e.g. to check price is really numeric.
* Data extracted and written to MongoDB collection
> * If required, Scrapy-MongoDB automatically populates timestamp as an ISODate in a nested field:
>> `"scrapy-mongodb" : {"ts" : ISODate("2014-02-06T10:13:20.268Z")}`
* Add product type information so we can process e.g. bread and dairy products separately.
* Now reads query criteria from a CSV file of "product_type","query" e.g. "BREAD","white sliced loaf 800g"
* Some problems with character-sets if CSV generated from Excel or OpenOffice: **use plain text editor instead!**
* Re-factored URL and XPath selection in spider - XPaths now provided via SaerchSettings class.
* Implemented different options for outputs i.e. CSV and/or MongoDB.
* Extended input CSV format to include base URL and sub-categories for search.
* Include ONS item number/name for matching back to Prices standard search list.
* Re-factored to use Tesco website categories instead of of basic search function.
* Now searches from Tesco Groceries page via a nested tree of search categories (3 levels).
* Handles paging through results.
* Implemented product item checks for search terms e.g. "white sliced 800g".
* Extract and format volume price where possible e.g. £1.23/100g.
* Re-factored code, removed obsolete spider classes.

### TO DO
* Expand list of products.
* Look at how to supply SearchSettings at runtime e.g. from a CSV file?
* Look at how to run multiple web-scraping tasks in a single session e.g. command-line API?
* Implement equivalent functionality for another supermarket (new spider).
* Start looking at how to feed daily/weekly scraped data to business (volumes?).

