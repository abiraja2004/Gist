import pytest
import time
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from selenium import webdriver
import webtest

import main

@pytest.fixture()
def setup_testbed(request):
    # First, create an instance of the Testbed class.
    my_testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    my_testbed.activate()
    # Next, declare which service stubs you want to use.
    policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1.0)
    my_testbed.init_memcache_stub()
    my_testbed.init_datastore_v3_stub(consistency_policy=policy)

    def teardown_testbed():
        my_testbed.deactivate()
    request.addfinalizer(teardown_testbed)

@pytest.fixture()
def setup_testapp(request, setup_testbed):
    testapp = webtest.TestApp(main.app)
    return testapp

@pytest.fixture(scope="module")
def setup_selenium(request):
    driver = webdriver.Firefox()
    time.sleep(1)

    def teardown_selenium():
        driver.quit()
    request.addfinalizer(teardown_selenium)

    return driver