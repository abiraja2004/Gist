"""
This module requires the same config.cfg as testallfast.py
"""

import testallfast
import pytest
import subprocess
import sys
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

APP_PATH = config.get("Unit Tests", "APP_PATH")

cmd = r'"'+sys.executable+'" "'+testallfast.GAE_PATH+'\dev_appserver.py" "'+APP_PATH+r'" -A gist-selenium --port=9999 --datastore_path=C:\tmp\selenium_datastore --clear_datastore=yes'
app_engine = subprocess.Popen(cmd)

pytest.main('-m "webtest or slowtest"')

app_engine.terminate()