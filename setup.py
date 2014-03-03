"""
setup.py
========
Based on example from Learn Python The Hard Way
(http://learnpythonthehardway.org/book/ex46.html)
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Scrapy Tesco Prototype',
    'author': 'Chris Webster',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'christopher.webster@ons.gov.uk',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['supermarket_scraper'],
    'scripts': [],
    'name': 'supermarket_scraper'
}

setup(**config)
