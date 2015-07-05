import urlparse
import userinput

from fixtures import *
from getreview import *

import pytest

URL = userinput.parse_url('http://www.test.com/example')

@pytest.fixture()
def setup_testbed_with_review(setup_testbed):
    Review.create_or_update_review('abc',URL,['omg'])

def test_create_new_review(setup_testbed_with_review):
    # Call create_or_update_review method
    # Get a review
    # Assert that there is a review
    review = Review.query().get()
    assert review is not None
  
def test_get_review_by_url(setup_testbed_with_review):
    review = Review.get_by_url(URL)
    assert review is not None
    
def test_get_review_by_name(setup_testbed_with_review):
    name = 'adc'
    review = Review.get_by_name(name)
    assert name is not None
    
def test_get_all_urls(setup_testbed_with_review):
    urls = Review.get_all_urls()
    assert len(urls) == 1
    assert userinput.parse_url(urls[0][0]) == URL
    

    
  

