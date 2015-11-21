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


def test_post_should_fail_if_api_key_is_wrong(client):
    rv = client.post('/{}-invalid'.format(API_KEY))
    assert rv.status_code == 403


def test_post_should_return_200_if_api_key_is_right(client):
    rv = client.post('/{}'.format(API_KEY))
    assert rv.status_code == 200
