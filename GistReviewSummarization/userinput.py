import urlparse
import logging
import traceback
import copy

from google.appengine.ext import deferred
from google.appengine.api import memcache

import yelpreviewscraper
import metacriticscraper
import getreview
from summarization import summarize
from summarization import optimize

class NotInDatabaseException(Exception):
    pass
class NotValidURLException(Exception):
    pass

TASK_KEY = 'updating_keypoints|{}'

def run_deferred_update(url):
    cache = memcache.get(TASK_KEY.format(url))
    if cache == None:
        deferred.defer(update_keypoints_from_url, url=url)
    else:
        pass

def update_keypoints_from_url(url):
    # TODO: only update review if it's old
    product_url = url.netloc+url.path
    try:
        error = None
        keypoints = []
        # Get reviews
        try:
            if(url.netloc == 'www.yelp.com'):
                logging.info("url.netloc == 'www.yelp.com'")
                name, reviews = yelpreviewscraper.get_reviews(product_url)
            elif(url.netloc == 'www.metacritic.com'):
                logging.info("url.netloc == 'www.metacritic.com'")
                name, reviews = metacriticscraper.get_reviews(product_url)
            
            if not reviews:
                raise ValueError('No reviews returned') # To force except block
        except:
            # Log traceback for debugging
            logging.error(traceback.format_exc())

            # Set error for user to see
            name = ''
            error = 'Cannot find reviews on page.'

        # Create keypoints
        if not error:
            try:
                keypoints = summarize.get_keypoints(reviews, name)
            except optimize.NotEnoughSentencesError:
                error = 'Not enough reviews to summarize.'

        # Store keypoints, or error
        # keypoints will be [] if error is set
        getreview.Review.create_or_update_review(name, url, keypoints, error=error)
    except Exception as error:
        logging.error('Failure in update keypoints task for url: {}'.format(product_url))
        logging.error(traceback.format_exc())
        return

def parse_url(url):
    if not url.startswith('http'):
        url = '%s%s' % ('http://', url)
    return urlparse.urlparse(url)

def handle_user_search(user_input):
    # Parse user input 
    url = parse_url(user_input)
    # If the url is invalid, set url_error in output
    # If url is valid, but result is not found, tell the user to wait
    # If the result is found, return the key_points
    if(url.netloc == 'www.yelp.com' or url.netloc == 'www.metacritic.com'):
        key_points = getreview.Review.get_by_url(url)
        if key_points is None:
            #start scraping
            run_deferred_update(url)
            raise NotInDatabaseException('URL not in database. Please wait.')
        if key_points.error is not None:
            raise NotValidURLException(key_points.error)
        return key_points
    else:
        raise NotValidURLException('Invalid URL: {}'.format(user_input))