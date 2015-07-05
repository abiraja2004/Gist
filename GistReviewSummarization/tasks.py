import datetime
import logging
import traceback
import urlparse

from google.appengine.ext import deferred
from google.appengine.api import memcache

import base
import getrestauranturls
import yelpreviewscraper
import metacriticscraper
from summarization import summarize
import getreview
import logging

# TODO: Use delay function (from other project) with 24 hour interval and offset by url to spread out these scraping tasks
class UpdateKeypointsHandler(base.Handler):
    """Generates and updates the database of keypoints."""
    def get(self):
        # Get a list of product urls
        # For each url, schedule a task to generate keypoints for the database
        new_urls = getrestauranturls.main()
        old_urls_times = getreview.Review.get_all_urls()
        old_urls = [url_time[0] for url_time in old_urls_times]

        # First check urls currently in database
        # Only update old ones
        logging.info('Checking {} urls from database'.format(len(old_urls_times)))
        num_old_updated = 0
        for url_time in old_urls_times:
            # If more than 30 days have passed
            if (datetime.datetime.now() - url_time[1]).days > 30:
                # Add task to queue
                url_object = urlparse.urlparse(url_time[0])
                deferred.defer(update_keypoints_from_url, url=url_object)
                num_old_updated += 1
        logging.info('{} urls from database updated'.format(num_old_updated))

        # Check for new urls, only update urls that are not in database
        logging.info('Checking {} urls from the web'.format(len(new_urls)))
        num_new_updated = 0
        for url in new_urls:
            if url not in old_urls: # This could use some optimization
                # Add task to queue
                url_object = urlparse.urlparse(url_time[0])
                deferred.defer(update_keypoints_from_url, url=url_object)
                num_new_updated += 1
        logging.info('{} urls from web updated'.format(num_new_updated))