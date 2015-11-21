import logging
import os
import pytest

API_KEY = 'fnord'
os.environ['SLIPSTREAM_API_KEY'] = API_KEY

from slipstream import slipstream

log = logging.getLogger('slipstream')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


# TODO: Module? Or not? -W. Werner, 2015-11-21
@pytest.fixture(scope="module")
def client():
    return slipstream.app.test_client()


def test_client_should_use_api_key():
    assert slipstream.app.config['API_KEY'] == API_KEY

