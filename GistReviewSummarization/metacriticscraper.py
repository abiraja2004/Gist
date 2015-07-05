#-------------------------------------------------------------------------------
# Name:        Meta Critic Web Scraper
# Purpose:      Gather reviews from metacritic page
#
# Author:      Thom Kitchen
#
# Created:     11/15/2015
# Last Modified: 03/26/2015
# Copyright:   (c) thom 2014
# Licence:     To Kill
#-------------------------------------------------------------------------------
import datetime
import logging
import traceback
import urllib3
import bs4

http = urllib3.PoolManager()

def get_reviews(url):
    """Get all reviews from a metacritic url, return as text.

    Args:
        url: A url, pointing to the reviews for a product on metacritic.

    Returns:
        2 strings as a tuple.  First element is the product name, second is the string of concatenated reviews
        name, reviews = get_reviews(some URL)
    """

#///////////////////////////////////////////////////////////////////////////////////////////////////////////
#//
#//      If metacritic changed their css selectors, find out what they are and rename these variables.
#//      You may have to change the html tag at the beginning of the findAll functions as well
#//
#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    review_css_selector = "reviews user_reviews"
    expanded_review = "blurb blurb_expanded"
    name_of_product = "product_title"
    next_page_css_selector = "flipper next"


#----------Empty string to hold reviews and bool to trigger cycle through pages of reviews
    reviews = ''
    has_next_page = False

#---------Call to webpage and feed page's dom into beautifulsoup to extract the reviews and product name
    try:
        response = http.request('GET', url, headers={'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"})
        soup = bs4.BeautifulSoup(response.data)
        review_body = soup.findAll('ol', {"class" : review_css_selector })
        for node in review_body:
            review_content = node.findAll('span', {"class" : expanded_review })

        product_info = soup.findAll('div', {"class" : name_of_product })
        for node in product_info:
            product_name = node.find('a').text

    #---Checks if there is a next page button. If so, set flag to true for a routine below to handle multiple pages
        next_page_button = soup.findAll('span', {"class" : next_page_css_selector })
        for node in next_page_button:
            if (node.find('a')!= None):
                has_next_page = True

    #-----Error check: CSS selector for reviews may have changed
        if(len(review_body)) == 0:
            print("An error has occured. No review content was found.")
            return

    #-------Copies content of the CSS selector for reviews into a string object
        review_count = 0
        for node in review_content:
                reviews += '\n' + node.text.strip() + '\n'
                review_count = review_count + 1

    #---Routine to handle multiple pages of reviews
        page_num = 1

        while has_next_page:
            has_next_page = False
            response = http.request('GET', (url + "?page=" + str(page_num)), headers={'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"})
            soup = bs4.BeautifulSoup(response.data)

            next_page_button = soup.findAll('span', {"class" : next_page_css_selector})
            for node in next_page_button:
                if (node.find('a')):
                    has_next_page = True

            review_body = soup.findAll('ol', {"class" : review_css_selector})
            for node in review_body:
                review_content = node.findAll('span', {"class" : expanded_review})
            for node in review_content:
                reviews += node.text + '\n\n'
            page_num = page_num + 1

        return product_name.strip(), reviews

    except Exception as error:
        logging.error('Unable to establish a connection for url: {}'.format(url))
        logging.error(traceback.format_exc())
        return



if __name__ == '__main__':
    name, content = get_reviews("http://www.metacritic.com/game/playstation-4/evolve/user-reviews")
    print(name + '\n' + content)
