import os
import datetime
import pytest
import tempfile
import textwrap
from unittest import mock
from slipstream import core
from slipstream import config

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


@pytest.yield_fixture(scope='module', autouse=True)
def temp_config():
    with tempfile.TemporaryDirectory() as content_dir, \
            tempfile.TemporaryDirectory() as output_dir, \
            mock.patch.dict(core.config,
                            {'CONTENT_DIR': content_dir,
                             'OUTPUT_DIR': output_dir,
                             'DEFAULT_AUTHOR': 'fnord@example.com',
                            }, clear=True):
        yield

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

def test_if_updated_header_is_present_it_should_be_used():
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
                                         Updated: {{:{}}}
                                        
                                         This should work...
                                         ''').format(fmt).format(timestamp))
        assert post.update_timestamp == timestamp


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


def test_if_no_author_is_provided_it_should_use_config_DEFAULT_AUTHOR():
    expected_author = 'roscivs@indessed.com'
    with mock.patch.dict(core.config, {'DEFAULT_AUTHOR': expected_author}):
        post = core.Post(textwrap.dedent('''\
                                         Title: there is no author

                                         So it should be set to a default.
                                         '''))
    assert post.author == expected_author


def test_a_post_created_with_author_should_use_it():
    expected_author = 'roscivs@example.com'
    post = core.Post(textwrap.dedent('''\
                                     Title: this is a title
                                     Author: {}

                                     The fourth, the fifth, the minor fall and the major lift
                                     ''').format(expected_author))
    assert post.author == expected_author


def test_a_post_created_from_the__str__of_the_other_they_should_have_the_same_properties():
    post_one = core.Post(textwrap.dedent('''\
                                         Title: This post has all the headers
                                         Date: 1982-06-25
                                         Updated: 2010-08-14
                                         Slug: this-is-slugtastic
                                         TaGs: do,  you, have,some,tags?
                                         AuThOr: foo@example.com

                                         This is a post, that's cool because
                                         <br> it has some html and

                                         - stuff
                                         - like markdown features
                                         - [so awesome](http://asdf.com)
                                         '''))
    post_two = core.Post(str(post_one))
    attrs = ('title', 'raw_content', 'publish_timestamp', 'update_timestamp',
             'author', 'tags')

    for attr in attrs:
        assert getattr(post_two, attr) == getattr(post_one, attr)


def test_when_tags_are_missing_they_should_be_empty_list():
    post = core.Post(textwrap.dedent('''\
                                     Title: There are no tags here

                                     So tags should be an empty list
                                     '''))
    assert post.tags is not None and post.tags == []


def test_when_tags_are_present_they_should_be_split_and_stripped():
    tags = ('something', 'cool', 'roscivs    ', '     bottia')
    expected_tags = [tag.strip() for tag in tags]

    post = core.Post(textwrap.dedent('''\
                                     Title: There are now tags
                                     TAgS: {}

                                     Of course the key will be normalized.''')
                                     .format(','.join(tags)))

    assert post.tags == expected_tags


def test_slugify_should_lowercase_text_and_convert_all_non_alphanumerics_to_one_hyphen():
    text = 'This is \t___---+++123456789!@#$%^&*()\'""\' some title'
    expected_text = 'this-is-123456789-some-title'

    assert core.slugify(text) == expected_text


def test_when_slug_header_is_not_provided_it_should_slugify_the_title():
    title = 'This is a title of which I have 1#$%@#$98089 "Great" Proudness'
    expected_slug = core.slugify(title)

    post = core.Post(textwrap.dedent('''\
                                     Title: {}

                                     Slugs are the sluggiest! Especially when
                                     they freelance...
                                     ''').format(title))

    assert post.slug == expected_slug


def test_changing_title_should_also_change_slug():
    title = 'This is a title of which I have 1#$%@#$98089 "Great" Proudness'
    expected_slug = core.slugify(title)

    post = core.Post(textwrap.dedent('''\
                                     Title: Title of Great Good

                                     Slugs are the sluggiest! Especially when
                                     they freelance...
                                     ''').format(title))
    post.title = title

    assert post.slug == expected_slug


def test_if_render_is_not_passed_a_jinja_template_it_should_use_the_one_from_the_config():
    mock_template = mock.MagicMock()
    with mock.patch.dict(core.config, {'POST_TEMPLATE': mock_template}):
        post = core.Post(GENERIC_GOOD_POST)
        post.render()

    mock_template.render.assert_called_with(post=post)


def test_if_render_is_not_passed_a_jinja_template_it_should_use_the_one_provided():
    mock_template = mock.MagicMock()
    used_template = mock.MagicMock()
    with mock.patch.dict(core.config, {'POST_TEMPLATE': mock_template}):
        post = core.Post(GENERIC_GOOD_POST)
        post.render(template=used_template)

    assert mock_template.render.call_count == 0
    used_template.render.assert_called_with(post=post)


def test_render_post_should_produce_result_of_template_render():
    expected_render = 'This is just something fake. <html>'
    mock_template = mock.MagicMock()
    mock_template.render.return_value = expected_render

    with mock.patch.dict(core.config, {'POST_TEMPLATE': mock_template}):
        post = core.Post(GENERIC_GOOD_POST)
        actual_render = post.render()

    assert actual_render == expected_render


def test_when_publish_is_called_it_should_save_the_post_using_config_CONTENT_DIR_and_slug():
    title = 'This is a title for great good'
    expected_filename = '{}.md'.format(core.slugify(title))
    with tempfile.TemporaryDirectory() as d, \
            mock.patch.dict(core.config, {'CONTENT_DIR': d}):
        core.publish(title=title,
                     content='This is a post that is for the awesome',
                     author='roscivs_bottia@example.com',
                    )

        assert expected_filename in os.listdir(d)


def test_when_publish_is_called_post_values_should_be_generated_from_saved_file():
    post_one = core.Post(textwrap.dedent('''\
                                         Title: This post has all the headers
                                         Date: 1982-06-25
                                         Updated: 2010-08-14
                                         Slug: this-is-slugtastic
                                         TaGs: do,  you, have,some,tags?
                                         AuThOr: foo@example.com

                                         This is a post, that's cool because
                                         <br> it has some html and

                                         - stuff
                                         - like markdown features
                                         - [so awesome](http://asdf.com)
                                         '''))
    attrs = ('title', 'raw_content', 'publish_timestamp', 'update_timestamp',
             'author', 'tags')

    with tempfile.TemporaryDirectory() as d, \
            mock.patch.dict(core.config, {'CONTENT_DIR': d}):

        core.publish(title=post_one.title,
                     content=post_one.raw_content,
                     author=post_one.author,
                     slug=post_one.slug,
                     tags=','.join(post_one.tags),
                    )
        print(os.listdir(d))
        with open(os.path.join(d, post_one.slug+'.md')) as f:
            text = f.read()
            print(text)
            post_two = core.Post(text)

    for attr in attrs:
        assert getattr(post_one, attr) == getattr(post_one, attr)


def test_publish_should_call_generate_index_and_pass_it_config_OUTPUT_DIR_and_CONTENT_DIR():
    with tempfile.TemporaryDirectory() as output_dir, \
            tempfile.TemporaryDirectory() as content_dir, \
            mock.patch.dict(core.config, {'OUTPUT_DIR': output_dir,
                                          'CONTENT_DIR': content_dir}):
        with mock.patch('slipstream.core.generate_index') as fake_gen_index:
            core.publish(title='blargle',
                         content='This is a post that is for the awesome',
                         author='roscivs_bottia@example.com',
                        )
            fake_gen_index.assert_called_with(content_dir=content_dir,
                                              output_dir=output_dir)


def test_publish_should_call_generate_tag_page_and_pass_it_each_tag_and_OUTPUT_DIR():
    with tempfile.TemporaryDirectory() as output_dir, \
            tempfile.TemporaryDirectory() as content_dir, \
            mock.patch.dict(core.config, {'OUTPUT_DIR': output_dir}):
        with mock.patch('slipstream.core.generate_tag_page') as fake_gen_tag_pages:
            expected_tags = [tag.strip()
                             for tag in 'these, are, my tags'.split(',')
                             ]
            core.publish(title='blargle',
                         content='This is a post that is for the awesome',
                         author='roscivs_bottia@example.com',
                         tags=','.join(expected_tags),
                        )
            for tag in expected_tags:
                fake_gen_tag_pages.assert_any_call(tag=tag,
                                                   output_dir=output_dir)


def test_if_post_is_not_tagged_then_publish_should_not_call_generate_tag_page():
    with mock.patch('slipstream.core.generate_tag_page') as fake_gen_tag_pages:
        core.publish(title='blargle',
                     content='This is a post that is for the awesome',
                     author='roscivs_bottia@example.com',
                     # No tags here...
                     )
        assert fake_gen_tag_pages.call_count == 0


def test_publish_should_call_generate_rss():
    with mock.patch('slipstream.core.generate_rss') as fake_gen_rss:
        core.publish(title='blargle',
                     content='This is a post that is for the awesome',
                     author='roscivs_bottia@example.com',
                     # No tags here...
                     )
        assert fake_gen_rss.call_count == 1


def test_publish_should_call_generate_atom_feed():
    with mock.patch('slipstream.core.generate_atom') as fake_gen_atom:
        core.publish(title='blargle',
                     content='This is a post that is for the awesome',
                     author='roscivs_bottia@example.com',
                     # No tags here...
                     )
        assert fake_gen_atom.call_count == 1


def test_if_publish_webhook_is_set_then_publish_should_pass_new_post_to_call_webhook():
    with mock.patch('slipstream.core.publish_webhook') as fake_publish_webhook,\
            mock.patch.dict(core.config, {'PUBLISH_WEBHOOK': 'http://example.com'}):
        core.publish(title='blargle',
                     content='This is a post that is for the awesome',
                     author='roscivs_bottia@example.com',
                     # No tags here...
                     )
        assert fake_publish_webhook.call_count == 1

    # See https://meta.discourse.org/t/discourse-api-documentation/22706


def test_if_publish_webhook_is_not_truthy_webhook_should_not_be_called():
    with mock.patch('slipstream.core.publish_webhook') as fake_publish_webhook,\
            mock.patch.dict(core.config, {'PUBLISH_WEBHOOK': None}):
        core.publish(title='blargle',
                     content='This is a post that is for the awesome',
                     author='roscivs_bottia@example.com',
                     # No tags here...
                     )
        assert fake_publish_webhook.call_count == 0


# TODO: Write tests for webhook -W. Werner, 2015-12-08
