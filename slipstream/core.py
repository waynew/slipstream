'''
The Slipstream file format is inspired by SMTP and Pelican.

The file format consists of a file with one or more key:value pairs, followed
by a blank line, followed by the body. An example file:

::
    title: So Long, and Thanks For All The Fish
    date: 2010-08-14

    They were delicious fish, weren't they?

Here is an example invalid file:

::
    title: I Just Can't Follow Directions
    I mean, really. How hard is it to have one blank line?
    Is it really that hard?

It's an invalid file because the second line has a space after ``I`` and no
``:``.

Valid keys are:

- ``title``: Any text. This will be the title (h1 or h2?) of the blog post.
- ``slug`` (Optional): This is how you want the url to be formed. If not
  present, the URL will simply be a replace of non-URL-safe characters with
  ``-``.
- ``date``: Any ``arrow.get``-parsable string, but keep it to something simple
  like 'YYYY-MM-DD', or 'YYYY-MM-DD HH:MM', mmkay? This is the date theat you
  wrote your post.
- ``updated``: When you updated your post.
- ``author``: The email address of the author. Doesn't have to be a *real*
  address - just as long as it has an `@` sign in it.
- ``tags``: Comma-delimited list of tags. e.g. ``these are, tags, okay``.


'''
import os
import re
from flask import current_app
from datetime import datetime
from textwrap import dedent
from . import config


class Post:
    def __init__(self, text, **more_headers):
        headers, body = self._parse_headers(text)
        headers.update(more_headers)
        if not body.strip():
            raise ValueError('Must add body text to post')

        self.title = headers['title']
        self.author = headers.get('author', config['DEFAULT_AUTHOR'])
        self.publish_timestamp = self._parse_date(headers.get('date'))
        if headers.get('updated') is None:
            self.update_timestamp = None
        else:
            self.update_timestamp = self._parse_date(headers.get('updated'))
        self.raw_content = body
        self.tags = [tag.strip() 
                     for tag in headers.get('tags', '').split(',')
                     if tag
                     ]
        self._slug = headers.get('slug')

    def __str__(self):
        optional_headers = []
        if self.update_timestamp:
            optional_headers.append(
                'Updated: {:%Y-%m-%d %H:%M}'.format(self.update_timestamp)
            )

        if self.tags:
            optional_headers.append('Tags: '+', '.join(self.tags))

        return dedent('''\
                      Title: {0.title}
                      Date: {0.publish_timestamp:%Y-%m-%d %H:%M}
                      Slug: {0.slug}
                      Author: {0.author}
                      {1}
                      {0.raw_content}'''
                      ).format(self, '\n'.join(optional_headers)+'\n')

    def _parse_headers(self, text):
        '''
        Return a dict of headers from the text. Text must have `key:value` 
        headers. A blank line signifies the end of the headers. Leading and
        trailing whitespace are stripped from all values.
        '''

        header_text, body = text.split('\n\n', maxsplit=1)
        headers = {}
        for header in header_text.split('\n'):
            key, value = header.split(':', maxsplit=1)
            headers[key.lower()] = value.strip()
        return headers, body

    def _parse_date(self, date):
        '''
        Parse the provided ``date`` into a ``datetime.datetime``. If ``date``
        is ``None``, return ``datetime.datetime.now()``.
        '''
        if date is None:
            return datetime.now()
        formats = ('%Y-%m-%d %H:%M:%S',
                   '%Y-%m-%d %H:%M',
                   '%Y-%m-%d',
                  )
        exc = None
        for fmt in formats:
            try:
                timestamp = datetime.strptime(date, fmt)
                break
            except ValueError as e:
                exc = e
        else:
            raise exc

        return timestamp

    @property
    def slug(self):
        return self._slug or slugify(self.title)

    def render(self, template=None):
        '''
        Return HTML-rendered version of the post. If ``template`` is provided,
        return the output of ``template.render(post=self)``, otherwise use the
        template in ``config['POST_TEMPLATE']``.
        '''
        template = template or config['POST_TEMPLATE']
        return template.render(post=self)


def slugify(text):
    '''
    Convert ``text`` to a suitable html string by replacing all 
    non-alphanumeric characters with a single hyphen ``-``.

    Examples:

    >>> slugify('The Quick Brown Fox Jumps Over The Lazy Dog')
    'the-quick-brown-fox-jumps-over-the-lazy-dog'
    >>> slugify("I'm such a 1337 h4><0r!!1!!")
    'i-m-such-a-1337-h4-0r1'
    >>> slugify('NaCl')
    'nacl'
    '''
    return re.sub(r'[^a-z0-9]+', '-', text.lower())


def publish(title, author, content, **headers):
    '''
    Publish stuff
    '''

    new_post = Post(dedent('''\
                       Title: {}

                       {}
                       ''').format(title, content), **headers)

    path_to_post = os.path.join(config['CONTENT_DIR'], new_post.slug+'.md')
    with open(path_to_post, 'w') as f:
        f.write(str(new_post))

    generate_index(content_dir=config['CONTENT_DIR'],
                   output_dir=config['OUTPUT_DIR'])

    for tag in new_post.tags:
        generate_tag_page(tag=tag, output_dir=config['OUTPUT_DIR'])

    generate_rss(content_dir=config['CONTENT_DIR'],
                 output_dir=config['OUTPUT_DIR'])

    generate_atom(content_dir=config['CONTENT_DIR'],
                  output_dir=config['OUTPUT_DIR'])

    if config.get('PUBLISH_WEBHOOK'):
        publish_webhook(new_post, config['PUBLISH_WEBHOOK'])


def generate_index(*, content_dir, output_dir):
    '''
    Generate index.html from the posts contained in content_dir``, saving the
    output in ``output_dir``. If files exist in the output_dir with the same
    name they will be overwritten.
    '''
    # TODO: Implement me -W. Werner, 2015-12-07


def generate_tag_page(*, tag, output_dir):
    '''
    Generate ``output_dir``/tag/``tag``.html that contains snippets and links
    to each of the posts that has the provided tag.
    '''
    # TODO: Implement me -W. Werner, 2015-12-07


def generate_rss(*, content_dir, output_dir):
    '''
    Generate ``output_dir/rss.xml`` RSS feed from the posts found in
    ``content_dir``

    # TODO: Only add an entry to the RSS feed -W. Werner, 2015-12-07
    '''


def generate_atom(*, content_dir, output_dir):
    '''
    Generate ``output_dir/atom.xml`` ATOM feed from the posts found in
    ``content_dir``

    # TODO: Only add an entry to the ATOM feed -W. Werner, 2015-12-07
    '''

def publish_webhook(*, post, webhook_url):
    '''
    POST ``post`` data to the provided webhook_url.
    '''
    # Right now I really only care about discourse, but I suspect it might be
    # nice to provide other endpoints
