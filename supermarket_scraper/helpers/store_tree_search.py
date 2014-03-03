# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 12:53:08 2014

@author: onsbigdata
"""
from supermarket_scraper.helpers.search_loader import SearchLoader

class StoreSearch(object):
    """Represents details of a particular product search at a given store."""
    
    def __init__(self, store):
        self.store = store
    
    def set_base_url(self, url):
        self.base_url = url

    def set_search_properties(self, props):
        """Set search properties based on input (from CSV). Default is ''."""
        self.ons_item_no = props.get('ons_item_no',-1)
        self.ons_item_name = props.get('ons_item_name','')
        self.base_url = props.get('base_url','') # URL quote?
        self.base_cat = props.get('base_cat','')
        self.store_sub1 = props.get('store_sub1','')
        self.store_sub2 = props.get('store_sub2','')
        self.store_sub3 = props.get('store_sub3','')
        self.search_terms = props.get('search_terms','')        
        
    # Allow arbitray paths to be set/accessed

    def set_path(self, pathname, path):
        self.paths[pathname] = path

    def get_path(self, pathname):        
        return self.paths.get(pathname,"")

    # Construct map of meta-data for passing around with Request/Response

    def get_meta_map(self):
        """Returns a map of the meta-data for the search, for passing around
           with the Request/Response as these are processed by the spider."""
        meta_map = {
                    'ons_item_no': self.ons_item_no,
                    'ons_item_name': self.ons_item_name,
                    'base_url': self.base_url,
                    'base_cat': self.base_cat,
                    'store_sub1':self.store_sub1,
                    'store_sub2':self.store_sub2,
                    'store_sub3':self.store_sub3,
                    'search_terms':self.search_terms
                    }
        return meta_map
    
    
    def __str__(self):
        """Default string representation."""
        s = "|".join([self.store , 
                      self.ons_item_no, self.ons_item_name,
                      self.base_url, self.base_cat,
                      self.store_sub1,self.store_sub2,self.store_sub3,
                      self.search_terms])
        return  s

class SearchNode(object):
    """Simple tree representation of searches.  Each node has:
       --> name e.g. Bakery
       --> data - optional dict of additional attributes
       --> children - list of child nodes 
       Using method add_child() should prevent duplicates."""
       
    def __init__(self, name, data ={}):
        self.name = name
        self.data = data
        self.children = []

    def find_child(self, name):
        """Return child with given name, or None."""
        for c in self.children:
            if c.name == name:
                return c
        return None
        
    def add_child(self, node):
        """Add a child node to this parent node.
           Checks if child already exists on this node (by name)."""
        c = self.find_child(node.name)
        if c:
            # append children of new node to existing child with same name
            for nc in node.children:
                c.add_child(nc)
        else:
            # append new child node as it does not yet exist on this node
            self.children.append(node)

    def as_dict(self):
        """Return a dictionary representation of the tree.
           Need this as we have to pass the tree around with the Request,
           so we need a transferable format.
        """
        d = {'name':self.name,'data':self.data}
        dc = [c.as_dict() for c in self.children]  
        d['children'] = dc
        return d
        
        
class SearchTreeFactory():
    """Produces a tree of SearchNodes."""
    
    def __init__(self,store=None,csv_file=None):
        self.csv_file = csv_file
        self.store = store

    def get_csv_searches(self):
        """Returns a LIST of StoreSearch instances based on records in CSV."""
        loader = SearchLoader()
        qs = loader.get_url_queries(self.csv_file)        
        #Build a search object for each query in the CSV file
        searches = []
        for q in qs:
            s = StoreSearch(self.store)
            s.set_search_properties(q)
            searches.append(s)
        return searches

    def get_csv_search_tree(self, tree_name):
        """Returns a TREE of search entries based on CSV file.
           Tree consists of nested sets of SearchNode instances.
           Search tree assumes 3 levels of sub-categories."""
        #First get all the searches as flat records
        searches = self.get_csv_searches()
        #Now build a tree from searches (add_child() avoids duplicates below)
        tree = SearchNode(tree_name)   
        for s in searches:
            # n3 is lowest-level node and will hold search data
            n3 = SearchNode(s.store_sub3, s.get_meta_map())
            # n2 - acts as immediate parent to n3 nodes
            n2 = SearchNode(s.store_sub2)
            n2.add_child(n3)
            # n1 - acts as immediate parent to n2 nodes
            n1 = SearchNode(s.store_sub1)
            n1.add_child(n2)
            # put n1 node onto tree
            tree.add_child(n1)       
        # Return the tree
        return tree

            
