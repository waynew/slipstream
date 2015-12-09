import json
import logging
import os
import pytest
import tempfile
from unittest import mock

API_KEY = 'fnord'
os.environ['SLIPSTREAM_API_KEY'] = API_KEY

from slipstream import slipstream

log = logging.getLogger('slipstream')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

SIMPLE_PAYLOAD = dict(
        id=42,
        name='This is a cool title',
        content='This is a blog post\nAnd it is *soo* cool',
        content_html='<html><h2>This is some markdown</h2></html>',
        user={'id': 42, 'email': 'test@example.com'},
        created_at='2010-08-14T09:23:12-05:00',
        updated_at='2010-08-14T09:23:12-05:00',
)


# TODO: Module? Or not? -W. Werner, 2015-11-21
@pytest.fixture(scope="module")
def client():
    return slipstream.app.test_client()


def test_client_should_use_api_key():
    assert slipstream.app.config['API_KEY'] == API_KEY


def test_post_should_fail_if_api_key_is_wrong(client):
    rv = client.post('/{}-invalid'.format(API_KEY))
    assert rv.status_code == 403


def test_post_should_pass_payload_to_core_publish(client):
    expected_id = 'Some document id thing'
    expected_title = 'The Ballad of Wol Emulov'
    expected_content = '## This is some markdown'
    expected_author = 'roscivs@indessed.com'
    payload = dict(
        id=expected_id,
        name=expected_title,
        content=expected_content,
        content_html='<html><h2>This is some markdown</h2></html>',
        user={'id': 42, 'email': expected_author},
        created_at='2010-08-14T09:23:12-05:00',
        updated_at='2010-08-14T09:23:12-05:00',
    )

    with mock.patch('slipstream.core.publish') as fake_publish:
        rv = client.post('/{}'.format(API_KEY), data={
            'payload': json.dumps(payload),
        })

        assert rv.status_code == 200
        fake_publish.assert_called_with(
            id=expected_id,
            title=expected_title,
            content=expected_content,
            author=expected_author,
        )


def test_publish_should_put_post_in_content_directory(client):
    with tempfile.TemporaryDirectory() as content_dir, \
         tempfile.TemporaryDirectory() as output_dir,  \
         mock.patch.dict(slipstream.app.config,
                         {'OUTPUT_DIR': output_dir,
                          'CONTENT_DIR': content_dir,
                          'DEFAULT_AUTHOR': 'test@example.com',
                         }),                           \
         mock.patch.dict(slipstream.core.config, slipstream.app.config):

        rv = client.post('/{}'.format(API_KEY), data={
            'payload': json.dumps(SIMPLE_PAYLOAD),
        })

        assert slipstream.core.slugify(SIMPLE_PAYLOAD['name'])+'.md' in os.listdir(content_dir)


def test_publish_should_put_post_in_content_directory(client):
    with tempfile.TemporaryDirectory() as content_dir, \
         tempfile.TemporaryDirectory() as output_dir,  \
         mock.patch.dict(slipstream.app.config,
                         {'OUTPUT_DIR': output_dir,
                          'CONTENT_DIR': content_dir,
                          'DEFAULT_AUTHOR': 'test@example.com',
                         }),                           \
         mock.patch.dict(slipstream.core.config, slipstream.app.config):

        rv = client.post('/{}'.format(API_KEY), data={
            'payload': json.dumps(SIMPLE_PAYLOAD),
        })

        assert slipstream.core.slugify(SIMPLE_PAYLOAD['name'])+'.md' in os.listdir(content_dir)
