import base64
import logging
import os
import pytest
import slipstream.util
import string
import struct
import tempfile
from contextlib import contextmanager
from hypothesis import given
from hypothesis.strategies import text, integers
from unittest import mock

log = logging.getLogger('slipstream')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

try:
    FileNotFoundError
except:
    FileNotFoundError = OSError


@contextmanager
def backup_file(filename):
    with tempfile.TemporaryFile(mode='w+') as bak:
        if not os.path.exists(filename):
            try:
                with open(filename, 'w+') as f:
                    yield f
            finally:
                try:
                    os.unlink(filename)
                except FileNotFoundError:
                    pass  # Whatever
        else:
            try:
                with open(filename, 'r+') as f:
                    bak.write(f.read())
                    f.seek(0)
                    yield f
            finally:
                bak.flush()
                bak.seek(0)
                with open(filename, 'w') as f:
                    f.write(bak.read())


@given(text(alphabet=string.printable, min_size=1))
def test_if_SLIPSTREAM_API_KEY_exists_it_should_be_used(monkeypatch, txt):
    expected_key = txt
    monkeypatch.setitem(os.environ, 'SLIPSTREAM_API_KEY', expected_key)
    
    actual_key = slipstream.util.get_api_key()
    assert actual_key == expected_key


def test_if_SLIPSTREAM_API_KEY_does_not_exist_and_SLIPSTREAM_API_KEYFILE_points_to_bad_file_it_should_FileNotFoundError(monkeypatch):
    try:
        monkeypatch.delitem(os.environ, 'SLIPSTREAM_API_KEY')
    except KeyError:
        pass  # Ok, ENV doesn't have that variable.

    # Make sure we have a file that doesn't exist
    with tempfile.NamedTemporaryFile(delete=True) as f:
        filename = f.name
    monkeypatch.setitem(os.environ, 'SLIPSTREAM_API_KEYFILE', filename)

    with pytest.raises(FileNotFoundError):
        slipstream.util.get_api_key()


@given(text(alphabet=''.join(string.printable.split()), min_size=1))
def test_if_SLIPSTREAM_API_KEY_does_not_exist_and_SLIPSTREAM_API_KEYFILE_points_to_good_file_it_should_use_that_key(monkeypatch, txt):
    expected_key = txt
    try:
        monkeypatch.delitem(os.environ, 'SLIPSTREAM_API_KEY')
    except KeyError:
        pass  # Ok, ENV doesn't have that variable.

    with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
        f.write(expected_key)
        f.flush()
        monkeypatch.setitem(os.environ, 'SLIPSTREAM_API_KEYFILE', f.name)

        actual_key = slipstream.util.get_api_key()

    assert actual_key == expected_key


@given(text(alphabet=''.join(string.printable.split()), min_size=1))
def test_if_no_env_vars_exist_but_api_key_exists_then_use_it(monkeypatch, txt):
    expected_key = txt
    for var in ('SLIPSTREAM_API_KEY', 'SLIPSTREAM_API_KEYFILE'):
        try:
            monkeypatch.delitem(os.environ, var)
        except KeyError:
            pass  # Ok, ENV doesn't have that variable.

    with backup_file('.slipstream_api_key') as f:
        print('writing {!r}'.format(expected_key))
        f.write(expected_key)
        f.truncate()
        f.close()

        actual_key = slipstream.util.get_api_key()

    assert actual_key == expected_key


@given(integers(max_value=9223372036854775))
def test_if_no_env_vars_exist_and_no_file_exists_it_should_be_created_and_urlsafe64encode_output_dumped_in(monkeypatch, num):
    print(num)
    expected_key = base64.urlsafe_b64encode(struct.pack('@l', num)).decode()
    for var in ('SLIPSTREAM_API_KEY', 'SLIPSTREAM_API_KEYFILE'):
        try:
            monkeypatch.delitem(os.environ, var)
        except KeyError:
            pass  # Ok, ENV doesn't have that variable.

    with mock.patch('slipstream.util.os.urandom') as fake_urandom:
        fake_urandom.return_value = struct.pack('@l', num)

        with backup_file('.slipstream_api_key') as f:
            os.unlink(f.name)

            actual_key = slipstream.util.get_api_key()
            key_in_file = open(f.name).read()

    assert actual_key == expected_key
    assert actual_key == key_in_file
