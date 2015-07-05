import hashlib
import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

class Review(ndb.Model):
    """A model containing keypoints and relevent attributes for a review.
    
    args:
        product_name: string
        url: string
        key_points: list of strings
    """
    product_name = ndb.StringProperty()
    url = ndb.StringProperty()
    error = ndb.StringProperty(required=False)
    key_points = ndb.StringProperty(repeated=True)
    
    time_modified = ndb.DateTimeProperty(auto_now_add=True)

    def __str__(self):
        string = u'{"product_name": "' +self.product_name +u'"'
        string = string +u', "url": "' +self.url +u'"'
        key_points_string = ''
        for key_point in self.key_points:
            key_points_string = key_points_string + key_point.strip(u'"').strip(u'\xa0') +u'|'
        string = string +u', "key_points": "' +key_points_string +u'"}'
        return string.encode('utf-8')

    def to_dict(self):
        response = {}
        response['product_name'] = self.product_name
        response['url'] = self.url
        key_points_list = []
        for key_point in self.key_points:
            key_points_list.append(key_point)
        response['key_points'] = key_points_list
        return response
    
    # This method search key points by product name.
    @classmethod
    def get_by_name(cls, product_name):
        """Get a review entity by the product name."""
        keys = "product_name|{}".format(product_name)
        # Search the memcache using the keys
        reviews = memcache.get(keys)
        # If key points excess in memcache, then return key points.
        if reviews is not None:
            return reviews
        # Else it will search database then return key points and add to memcache
        else:
            reviews = Review.query(Review.product_name == product_name).fetch(10)
            if not memcache.add(keys,reviews):
                logging.error('Memcache set failed.')
            return reviews
    
    # This method search key points by url.
    @classmethod
    def get_by_url(cls, url):
        """Get a review entity by the url.
        
        The url is where the origional reviews were obtained from.
        """
        product_url = url.netloc+url.path
        # The memcache set doesn't work, gets 'Memcache set failed.' every time
        keys = "url|{}".format(product_url)
        # Search the memcache using the keys
        reviews = memcache.get(keys)
        # If key points excess in memcache, then return key points.
        if reviews is not None:
            return reviews
        # Else it will search database then return key points and add to memcache
        else:
            review = Review.query(Review.url == product_url).get()
            if not memcache.add(keys,review):
                pass
                #logging.error('Memcache set failed.')
            return review
            
    @classmethod
    def create_or_update_review(cls, product_name, url, key_points, error=None):
        review = cls.get_by_url(url)
        product_url = url.netloc + url.path
        if review == None:
            review = Review(product_name = product_name, url = product_url)
        review.key_points = key_points
        review.error = error
        review.put()
    
    @classmethod
    def get_all_urls(cls):
        qry = Review.query()
        url_projections = qry.fetch(1000,projection=[Review.url, Review.time_modified])
        return [(url_projection.url, url_projection.time_modified) for url_projection in url_projections]
    
    
