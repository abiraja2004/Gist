#-------------------------------------------------------------------------------
# Name:        Get Restaurants
# Purpose:  Gather urls of yelp pages across the country to build our data base of reviews
#
# Author:      thom
#
# Created:          02/07/2015
# Last Modified:    03/03/2015
#
# Copyright:   (c) thom 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import urllib3
import bs4
import cities
import time
import yelpreviewscraper as scraper

http = urllib3.PoolManager()

def main():
    restaurant_yelp_page = []
    city_urls = get_city_urls();
    for e in city_urls:
        for each in get_business_urls(e):
            restaurant_yelp_page.append(each)
        time.sleep(0.5)
    
    with open("restaurant_urls.txt", 'w') as f:
        for url in restaurant_yelp_page:
            f.write(url + '\n')
        f.close()
    
    return restaurant_yelp_page

def get_city_urls():
    """Get's the links to the yelp search results for the 3 most populous cities in each state

    Args:
        None

    Returns:
        Array of Yelp search result urls
    """
    states = ['AL', 'AK' ,'AZ' ,'AR' ,'CA' ,'CO' ,'CT' ,'DE' ,'FL' ,'GA' ,'HI', 'ID' ,'IL' ,'IN' ,'IA' ,'KS' ,'KY' ,'LA' ,'ME' ,'MD' ,'MA', 'MI' ,'MN' ,'MS' ,'MO' ,'MT' ,'NE' ,'NV' ,'NH' ,'NJ' ,'NM', 'NY' ,'NC' ,'ND' ,'OH' ,'OK' ,'OR' ,'PA' ,'RI' ,'SC' ,'SD', 'TN' ,'TX' ,'UT' ,'VT' ,'VA' ,'WA' ,'WV' ,'WI' ,'WY']
    list_of_cities = cities.main()
    x = 0 #Used to test if 3 cities have been added to increment to the next state
    city_url = []
    for e in list_of_cities:
        if list_of_cities.index(e) % 3 == 0:
            x = x + 1
            if list_of_cities.index(e) == 0:
                x = 0
        state_abbreviation = states[x]
        yelp_url = 'http://www.yelp.com/search?cflt=restaurants&find_loc=' + e +'%2C+' + state_abbreviation +'%2C+USA'
        city_url.append(yelp_url)
    return city_url

def get_business_urls(url):
    """Get all urls from page

    Args:
        url: A url, pointing to the reviews for a product on yelp.

    Returns:
        Array; all URLs on page.
    """
    base_url = "http://www.yelp.com"
    response = http.request('GET', url)
    soup = bs4.BeautifulSoup(response.data)
    links = []
    for a in soup.select('span.indexed-biz-name a[href^=/biz]'):     #------- Retrieving the href from the div the link to the restaurants yelp page is found
        links.append(base_url + str(a.attrs.get('href')))
    return links
    
def scrape_yelp_reviews():
    urls = []
    
    with open('restaurant_urls.txt', 'r') as f:
        urls = f.readlines()
        f.close()
        
    with open('restaurant_reviews.txt', 'w') as f:
        for url in urls:
            url = url[:-1]
            print 'Scraping: "%s"' % url
            for s in scraper.get_reviews(url):
                f.write(s.encode('ascii', 'ignore'))
            f.write('\n\n')    
            time.sleep(0.5)
            print '\tDone'
        f.close()

if __name__ == '__main__':
    scrape_yelp_reviews()




