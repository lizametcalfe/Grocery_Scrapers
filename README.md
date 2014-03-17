ONS Big Data: Web scraping prices
=================================
Overview
--------
* Initial prototype for web-scraping price information from public supermarket websites.  
* Installation tips below assume you are working on a Ubuntu/Debian-based Linux system e.g. Ubuntu, Linux Mint etc.  
* You may also be prompted to download dependencies in some cases.

Software
--------
### Required
The following are needed to run the basic web-scraping process (on Linux):

* Linux Mint (recommended)
* Python 2.7.x (should already be installed on any modern Linux system)
* Python PIP package installer e.g. on Ubuntu/Debian run:  
> `sudo apt-get install python-pip`
* Scrapy web-scraping framework e.g. 
> `sudo pip install Scrapy`
* Git (source code management) client to access code in remote repository (BitBucket) e.g.
> `sudo apt-get install git`
* You can then install the application code via Git `clone` from your BitBucket account.

### Optional
The following tools are optional, depending on whether you want to store your data in MongoDB, use Git version control, etc.

* Nose - testing framework for Python e.g.
> `sudo pip install nose`
* MongoDB database e.g.
> `sudo apt-get install mongodb`
* Python dependencies for PyMongo:
> `sudo apt-get install build-essential python-dev`
* PyMongo database driver e.g.
> `sudo pip install pymongo`
* scrapy-mongodb add-on to write Scrapy output straight to MongoDB e.g.
> `sudo pip install scrapy-mongodb`
* Gedit text-editor with Markdown plugin e.g.
> `sudo apt-get install gedit`
* Robomongo GUI client for MongoDB.  Download .DEB package and install using package manager.

Inputs: see `supermarket_scraper/input`
-------------------------------------
* The list of products to scrape is held in a CSV file in the `supermarket_scraper/input` directory e.g.:
>`supermarket_scraper/input/tesco_input.csv`
* The default file name is assumed to be `[spider name]_input.csv` as shown above.

* You can tell Scrapy the name of this product list input file at runtime:
>`scrapy crawl tesco -a csv_file=tesco_input.csv`
* If the filename is not provided at runtime, the program looks for a default file e.g. `tesco_input.csv` in the default location `supermarket_scraper/input`.

Outputs - see `supermarket_scraper/output`
--------------------------------------------
* Scrapy allows us to define ITEM_PIPELINES to send the items down a "pipe" for further processing.
* These are enabled via `supermarket_scraper/settings.py`.
* We have implemented several pipelines:
> * Price pipeline cleans up price entry. **ALWAYS RUN THIS**.
> * CSV pipeline writes data to a CSV file in the `supermarket_scraper/output` directory.
> * MongoDB pipeline writes item to MongoDB database if required.
* CSV output file names include a timestamp.  For example:
> `tesco_products_20140302132432.csv`

Usage
-----
### Running Scrapy with the Tesco spider
* Start in the top-level directory of the project e.g.:
>`cd myprojects/supermarket_scraper`
* If you want to run the Tesco spider with default input/output files, you can do so:
>`scrapy crawl tesco`
* The list of products to scrape is held in a CSV file in the `supermarket_scraper/input` directory e.g.:
>`supermarket_scraper/input/tesco_input.csv`
* You can also tell Scrapy the name of this product list input file at runtime:
>`scrapy crawl tesco -a csv_file=tesco_input.csv`
* If the filename is not provided at runtime, the program looks for the default file `tesco_input.csv` in the default location `supermarket_scraper/input`.

* You can also provide a relative path to the output directory (which **must exist**) at runtime:
>`scrapy crawl tesco -a csv_file=tesco_input.csv -a output_dir=output`
* This will write any output files to this directory (the default directory name is `output`):
>`supermarket_scraper/output`
* The output formats (CSV and/or MongoDB currently) are specified via the "pipeline" settings in `settings.py` (see "Outputs" above).
### Running Scrapy with the Waitrose spider
* As above, but use the spider name `waitrose` instead:
>`scrapy crawl waitrose`
* The input/output files will be in the same default directories and format as for the Tesco spider.
* However, the detailed URLs and sub-categories will be different as these are specific to each website.

Functionality
-------------
### Current
* Scrapes data for a number of products from Tesco or Waitrose website.
* **No validation** on data currently e.g. to check price is really numeric.
* Data can be extracted and written to CSV output file.
* Data can be extracted and written to MongoDB collection.
* Searches supermarket site by navigating 3 levels of (nested) menus then executing a product search.
* **All products are retrieved** for a given search i.e. no further filtering is applied at this stage.
* Handles paging through results.
* Looks for search terms e.g. "white sliced 800g" in the product description.
* Matching search terms are indicated via a simple metric e.g. if 1 term out of 2 matches the product description, then the search value is set to 0.5.
* Extracts and formats volume price where possible e.g. "£1.23/100g", "£10.00/10x440ml", "89p each".
* Calculates a standardised price per kg, litre or item.

### TO DO
* Fix bugs!
* Expand list of products.
* Look at how to run multiple web-scraping tasks in a single session e.g. command-line API?
* Improve robustness/reliability of price extraction/formatting?
* Start looking at how to feed daily/weekly scraped data to business (volumes?).

