#-------------------------------------------------------------------------------
# Name:        Yelp Review Scraper
# Purpose:      Gather reviews from yelp page
#
# Author:      Thom Kitchen
#
# Created:     10/29/2014
# Last Modified: 03/26/2015
# Copyright:   (c) thom 2014
# Licence:     To Kill
#-------------------------------------------------------------------------------

import urllib3
import bs4
import sys
import datetime
import dateutil.relativedelta

http = urllib3.PoolManager()



def get_reviews(main_yelp_page):
    """Get all reviews from a yelp url, return as text.

    Args:
        url: A url, pointing to the reviews for a product on yelp.

    Returns:
        List[2]: First element is the product name.  Second element is a string containing all reviews.
    """
    url = main_yelp_page

#///////////////////////////////////////////////////////////////////////////////////////////////////////////
#//
#//      If Yelp changed their css selectors, find out what they are and rename these variables.
#//      You may have to change the html tag at the beginning of the findAll functions as well
#//
#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    next_page_css_selector = "page-option prev-next next"
    review_css_selector = "review-content"
    product_name_tag_and_selector = "h1.biz-page-title"      #For this one, first is the html tag then . then the class name
    date_tag_id = "datePublished"
    actual_review_content_selector = "description"



#----------Empty string to hold reviews and bool to trigger cycle through pages of reviews
    reviews = ''
    has_next_page = False
#---------The calls to the web page and feeding those results into BeautifulSoup searching for reviews and next page button. Added exception handling
    try:
        response = http.request('GET', url)
    except urllib3.exceptions.HTTPError, e:
        print('HTTPError = ' + str(e))
        return
    except Exception, e:
        print("Error = " + str(e))
        return

    soup = bs4.BeautifulSoup(response.data)
    next_page_button = soup.findAll('a', {"class" : next_page_css_selector})
    review_info = soup.findAll('div', {'class' : review_css_selector})

#--------grab the product name to return in a list along with the reviews

    product_name = soup.select(product_name_tag_and_selector)[0].text


#-----Error check: CSS selector for reviews. may have changed
    if(len(review_info)) == 0:
        print("An error has occured. No review content was found.")
        return

#----Check if there is a next page button, if so execute routine to handle multiple pages
    if len(next_page_button) != 0:
        has_next_page = True

#-------parse through review_info for desired elements
    number_of_reviews = 0
    for node in review_info:
            review_date = node.find('meta', {"itemprop" : date_tag_id})['content']
            today = datetime.datetime.today()
            date_difference = today - dateutil.relativedelta.relativedelta(months=12)

            if (review_date > date_difference.isoformat()):
                review_content = node.findAll('p', {"itemprop" : actual_review_content_selector})
                reviews += review_content[0].text + '\n\n'
                number_of_reviews = number_of_reviews + 1

#----Routine for handling multiple pages of reviews to concat all into a single string object
    page_num = 1
    while has_next_page:
        response = http.request('GET', (url + "?start=" + str(page_num*40)))
        soup = bs4.BeautifulSoup(response.data)

        next_page_button = soup.findAll('a', {"class" : next_page_css_selector})

        review_info = soup.findAll('div', {'class' : review_css_selector})
        for node in review_info:
            review_date = node.find('meta', {"itemprop" : date_tag_id})['content']
            today = datetime.datetime.today()
            date_difference = today - dateutil.relativedelta.relativedelta(months=12)
            if (review_date > date_difference.isoformat()):
                review_content = node.findAll('p', {"itemprop" : actual_review_content_selector})
                reviews += review_content[0].text + '\n\n'
                number_of_reviews = number_of_reviews + 1

        if len(next_page_button) == 0:
            has_next_page = False
        page_num = page_num + 1
    return product_name.strip(), reviews

if __name__ == '__main__':

    name, review = get_reviews("http://www.yelp.com/biz/no-problemo-new-bedford")
    print(name + '\n\n' + review)


