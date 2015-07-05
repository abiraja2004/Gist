import pytest

from fixtures import *
from tasks import *

# This test performs a lot of calls to yelp
# best not to tempt them to ban your ip
@pytest.skip
@pytest.mark.slowtest()
def test_update_keypoints_handler(setup_testapp):
    testapp = setup_testapp

    # Run the task
    testapp.get('/tasks/updatekeypointdatabase')