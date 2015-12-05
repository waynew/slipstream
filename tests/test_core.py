import datetime
import pytest
import textwrap
from unittest import mock
from slipstream import core

GENERIC_GOOD_POST = '''\
Title: good posting

This is a good post. I swear it.'''

@pytest.fixture
def constant_time(request):
    fake_time = datetime.datetime(2010, 8, 14)
    datetime_patcher = mock.patch.object(
        core, 'datetime',
        mock.Mock(wraps=datetime.datetime)
    )
    def fin():
        datetime_patcher.stop()
    request.addfinalizer(fin)
    mocked_datetime = datetime_patcher.start()
    mocked_datetime.now.return_value = fake_time
    return fake_time


def test_creating_a_Post_should_ValueError_if_headers_are_malformed():
    with pytest.raises(ValueError):
        core.Post('there is no key\n\nhere')


def test_creating_a_Post_should_ValueError_if_there_is_no_header():
    with pytest.raises(ValueError):
        core.Post('no content here')


def test_creating_a_Post_should_ValueError_if_the_body_of_the_post_is_missing_or_empty():
    with pytest.raises(ValueError):
        core.Post('key: value\n\n')


def test_creating_a_Post_should_KeyError_if_there_is_no_title():
    with pytest.raises(KeyError):
        core.Post('key: value\n\nThere is no title here')


def test_creating_a_Post_should_work_with_keys_of_any_case():
    core.Post('Title: this should work\n\nIt really should')
    core.Post('TiTlE: this should work\n\nIt really should')


def test_creating_a_Post_should_use_the_provided_title_header():
    expected_title = 'this should work'
    post = core.Post('TiTlE: {}\n\nIt really should'.format(expected_title))
    assert post.title == expected_title


def test_if_no_publish_date_is_provided_it_should_use_current_date(constant_time):
    post = core.Post('Title: something with no date\n\nThere is no time')
    assert post.publish_timestamp == constant_time


def test_if_no_update_date_is_present_it_should_be_None():
    post = core.Post('Title: something with no date\n\nThere is no time')
    assert post.update_timestamp is None


def test_if_date_is_present_it_should_be_used_for_publish_timestamp():
    expected_time = datetime.datetime.now().replace(microsecond=0)
    formats = ('%Y-%m-%d %H:%M:%S',
               '%Y-%m-%d %H:%M',
               '%Y-%m-%d',
               )
    times = (expected_time,
             expected_time.replace(second=0),
             expected_time.replace(minute=0, hour=0, second=0),
             )
    for fmt, timestamp in zip(formats, times):
        post = core.Post(textwrap.dedent('''\
                                         Title: This is a title
                                         Date: {{:{}}}
                                        
                                         This should work...
                                         ''').format(fmt).format(timestamp))
        assert post.publish_timestamp == timestamp


def test_when_publish_is_called_it_should_save_the_post():
    pytest.skip()


def test_slugify_should_convert_all_non_alphanumerics_to_one_hyphen():
    pytest.skip()


def test_when_slug_header_is_not_provided_it_should_slugify_the_title():
    pytest.skip()


def test_when_author_is_missing_it_should_use_author_from_config():
    pytest.skip()


def test_when_tags_are_missing_they_should_be_empty():
    pytest.skip()


def test_a_post_created_from_the__str__of_the_other_they_should_have_the_same_properties():
    pytest.skip()


def test_if_render_is_not_passed_a_jinja_template_it_should_use_the_one_from_the_config():
    pytest.skip()


def test_render_post_should_produce_CommonMark_rendered_body_passed_to_jinja_template():
    pytest.skip()


## This is what Draft posts as the form 'payload' parameter (stringified, of course):
#{   
#        "id": your_document_id,
#        "name": "The Name of your Document",
#        "content": "The plain-text markdown of your document",
#        "content_html": "Your document rendered as HTML",
#        "user": {
#                    id: 1, 
#                    email: 'usersemail@example.com'
#                },
#        "created_at": "2013-05-23T14:11:54-05:00",
#        "updated_at": "2013-05-23T14:11:58-05:00"
#}
#
# json.loads


# TODO: Something about publishing here
#        core.publish(id=payload['id'],
#                     title=payload['name'],
#                     content=payload['content'],
#                     author=payload['user']['email'],

def test_if_publish_title_is_not_blank_it_should_add_title_header_to_content_before_creating_post():
    pytest.skip()


def test_if_author_is_not_blank_it_should_add_author_header_to_content_before_creating_post():
    pytest.skip()


def test_publish_should_save_post_in_content_directory():
    pytest.skip()


def test_publish_should_call_generate_index_and_pass_it_config_index_filename():
    pytest.skip()


def test_if_post_is_not_tagged_then_publish_should_not_call_generate_tag_page():
    pytest.skip()


def test_publish_should_call_generate_tag_page_with_each_tag_on_the_post():
    pytest.skip()


def test_publish_should_call_generate_rss():
    pytest.skip()


def test_publish_should_call_generate_atom_feed():
    pytest.skip()


def test_if_publish_webhook_is_set_then_publish_should_pass_new_post_to_call_webhook():
    pytest.skip()

    # See https://meta.discourse.org/t/discourse-api-documentation/22706
