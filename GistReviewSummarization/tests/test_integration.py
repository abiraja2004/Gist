import selenium

from fixtures import *
from ajax import *

import time
import pytest
URL = 'http://www.yelp.com/biz/lollys-cafe-new-bedford'
InvalidURL = 'http://www.tutorialspoint.com/python/list_len.htm'
    
@pytest.mark.webtest
def test_setup_selenium_with_invalid_url(setup_selenium):
    driver = setup_selenium
    driver.get("http://localhost:9999")  
    elem = driver.find_element_by_id("searchbar-text-field")   
    elem.send_keys(InvalidURL)
    elem.submit()
    time.sleep(0.5)

    error = driver.find_element_by_id("exception").text
    assert 'Invalid URL' in error
    #keys_point = driver.find_element_by_id("results-list").text
    #assert len(keys_point) == 0

@pytest.mark.webtest
def test_setup_selenium_test_if_URL_in_database(setup_selenium):
    driver = setup_selenium
    driver.get("http://localhost:9999")  
    elem = driver.find_element_by_id("searchbar-text-field")   
    elem.send_keys(URL)
    elem.submit()
    time.sleep(0.5)

    # Precondition
    error = driver.find_element_by_id('exception').text
    assert 'please wait' in error.lower()

    # Spin wait for key points
    for i in range(60):
        key_points = driver.find_elements_by_class_name("key-point")
        if len(key_points) > 0:
            break
        time.sleep(1)
        
    # Post condition
    assert len(key_points) == 3
    
#spin wait after delay function is added

@pytest.mark.webtest
def test_setup_selenium_with_url(setup_selenium):
    driver = setup_selenium
    driver.get("http://localhost:9999")  
    elem = driver.find_element_by_id("searchbar-text-field")   
    elem.send_keys(URL)
    elem.submit()
    time.sleep(0.5)

    # Doesn't ask user to wait
    with pytest.raises(selenium.common.exceptions.NoSuchElementException):
        error = driver.find_element_by_id('exception')

    #elem.send_keys(Keys.RETURN) 
    #assert "No results found." not in driver.page_source
    key_points = driver.find_elements_by_class_name("key-point")
    assert len(key_points) == 3