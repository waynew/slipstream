import base64
import logging
import os

log = logging.getLogger(__name__)


def get_api_key():
    '''
    Get API key from environment, file system, or generate it if not found.

    Look first in the environment variable ``SLIPSTREAM_API_KEY``. If that is
    not found, then check for ``SLIPSTREAM_API_KEYFILE``.  If the
    ``SLIPSTREAM_API_KEYFILE`` *does* exist and it is not a file, raise
    ``FileNotFoundError`` on python3, ``IOError`` on python2.  If that variable
    does not exist then look for a file named `.slipstream_api_key` in the
    current directory.

    If that file does not exist, attempt to create it and insert a random
    32-bit url-safe base64 encoded string.
    '''

    key = os.environ.get('SLIPSTREAM_API_KEY')
    if key is None:
        log.info('No SLIPSTREAM_API_KEY')
        filename = os.environ.get('SLIPSTREAM_API_KEYFILE')
        if filename is not None:
            log.info('SLIPSTREAM_API_KEYFILE=%r', filename)
            with open(filename) as keyfile:
                key = keyfile.read()
        else:
            filename = '.slipstream_api_key'
            log.info('No SLIPSTREAM_API_KEY* vars found,'
                     ' trying %r', filename)
            with open(filename, 'a+') as keyfile:
                keyfile.seek(0)
                key = keyfile.read()
                if not key:
                    log.info('No key found in file, generatig key')
                    keyfile.write(
                        base64.urlsafe_b64encode(os.urandom()).decode()
                    )
                    keyfile.flush()
                    keyfile.seek(0)
                    key = keyfile.read()

    return key
