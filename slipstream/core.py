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
from datetime import datetime


class Post:
    def __init__(self, text):
        headers, body = self._parse_headers(text)
        if not body.strip():
            raise ValueError('Must add body text to post')

        self.title = headers['title']
        self.publish_timestamp = self._parse_date(headers.get('date'))
        self.update_timestamp = None

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


def publish():
    '''
    Publish stuff
    '''
