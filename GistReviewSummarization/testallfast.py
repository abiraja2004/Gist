"""
This module requires a config.cfg file in the same folder.
Example config.cfg:

[Unit Tests]
GAE_PATH: C:\Program Files (x86)\Google\google_appengine
APP_PATH: C:\Users\JLove\Google Drive\Projects\GistReviewSummarization\Code\GistReviewSummarization
"""

import pytest
import doctest
import sys
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

GAE_PATH = config.get("Unit Tests", "GAE_PATH")
sys.path.insert(0, GAE_PATH)

pytest.main('-m "not webtest and not slowtest"')

from summarization import summarize

doctest.testmod(summarize)