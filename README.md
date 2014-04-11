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
* Python dependencies for Scrapy and PyMongo:
> `sudo apt-get install build-essential python-dev`
* Scrapy web-scraping framework e.g. 
> `sudo pip install Scrapy`
* Git (source code management) client to access code in remote repository (BitBucket) e.g.
> `sudo apt-get install git`
* You can then install the application code via Git `clone` from your BitBucket account (see below).

### Optional
The following tools are optional, depending on whether you want to store your data in MongoDB or Google Drive, use Git version control, etc.

* Nose - testing framework for Python e.g.
> `sudo pip install nose`
* MongoDB database e.g.
> `sudo apt-get install mongodb`
* PyMongo database driver e.g.
> `sudo pip install pymongo`
* scrapy-mongodb add-on to write Scrapy output straight to MongoDB e.g.
> `sudo pip install scrapy-mongodb`
* Gedit text-editor with Markdown plugin e.g.
> `sudo apt-get install gedit`
* PyDrive client API for Google Drive
> `sudo pip install PyDrive`

### Get the application code from BitBucket using the Linux Git client
* You need a free account on BitBucket.
* Ask the developers to enable access to the repository for your BitBucket user e.g. "onsfred".
* Once they've granted access, you should be able to clone the repository to create a local copy on your machine as follows.
* Open a Linux terminal and navigate to where you want to create the project files e.g.:
> `cd ~/myprojects`
* Check your BitBucket account home page and click on the entry for "supermarket_scraper" under "Repositories" (lower right).
* You should now see a repository page, with a "Clone" dropdown button near the top right.
* Click on this "Clone" dropdown, and select "HTTPS".
* This should display a Git command like this (assuming your BitBucket user is "onsfred"):
> `git clone https://onsfred@bitbucket.org/cmhwebster/supermarket_scraper.git`
* Copy this command and run it from the Linux command line.
* You will be prompted to enter your BitBucket password, then let Git download the code.
* Once this process has completed, you should have a local copy of the code in the `supermarket_scraper` directory.
* If you need to refresh your copy of the code to include later changes, you can do a Git "pull" within the project:
> * `cd ~/myprojects/supermarket_scraper`
> * `git pull`
* You will be prompted for your BitBucket password, then Git will update your copy of the code with any changes.

Inputs: see `supermarket_scraper/input`
-------------------------------------
* The list of products to scrape is held in a CSV file in the `supermarket_scraper/input` directory e.g.:
>`supermarket_scraper/input/tesco_input.csv`
* The default file name is assumed to be `[spider name]_input.csv` as shown above.

* You can tell Scrapy the name of this product list input file at runtime:
>`scrapy crawl tesco -a csv_file=tesco_input.csv`
* If the filename is not provided at runtime, the program looks for a default file e.g. `tesco_input.csv` in the default location `supermarket_scraper/input`.

Outputs - see `supermarket_scraper/output`
------------------------------------------
* Scrapy allows us to define ITEM_PIPELINES to send the items down a "pipe" for further processing.
* These are enabled via `supermarket_scraper/settings.py`.
* We have implemented several pipelines:
> * Price pipeline cleans up price entry. **ALWAYS RUN THIS**.
> * CSV pipeline writes data to a CSV file in the `supermarket_scraper/output/[spider]` directory.
> * MongoDB pipeline writes item to MongoDB database if required.
* CSV output file names include a timestamp.  For example:
> `tesco_products_20140302132432.csv`
* CSV output files are written to the `supermarket_scraper/output/[spider]` directory. For example:
> `supermarket_scraper/output/tesco/tesco_products_20140302132432.csv`

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
* The output formats (CSV and/or MongoDB currently) are specified via the "pipeline" settings in `settings.py` (see "Outputs" above).
* The CSV output file will be in `supermarket_scraper/output/tesco`.
### Running Scrapy with the Waitrose spider
* As above, but use the spider name `waitrose` instead:
>`scrapy crawl waitrose`
* The input file will be in the same default directory and format as for the Tesco spider.
* However, the detailed URLs and sub-categories will be different as these are specific to each website.
* The CSV output files will be in `supermarket_scraper/output/waitrose`, and the data will be in the same format as for the Tesco spider.


