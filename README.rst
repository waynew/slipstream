===============================
Slipstream
===============================

.. TODO add these badges back, \o/
.. .. image:: https://badge.fury.io/py/draftin_a_flask.png
    :target: http://badge.fury.io/py/draftin_a_flask
    
.. .. image:: https://travis-ci.org/waynew/draftin-a-flask.png?branch=master
        :target: https://travis-ci.org/waynew/draftin-a-flask

.. .. image:: https://pypip.in/d/draftin_a_flask/badge.png
        :target: https://crate.io/packages/draftin_a_flask?version=latest

Slipstream is a cool tool that allows you to generate static blogs from
`Draft`_ `WebHooks`_

.. _Draft: http://draftin.com
.. _WebHooks: https://draftin.com/documents/69898?token=5fjKKlZ0-AeBzqj_RAftAGdzRzl9VBfBHj5wpSWm_gU


Quickstart (Easiest Version)
----------------------------

Run the following commands:

::

    $ docker run -d --name slipstream -p '0.0.0.0:5000:5000' \
      -e SLIPSTREAM_OUTPUT_DIR='/usr/share/nginx/html' waynew/slipstream
    $ docker run -d --name webserver --volumes-from slipstream \
      -p '0.0.0.0:8080:80' nginx
    $ docker logs --tail=1 slipstream
    Api Key: vsup5kabBC5Qen2ADH1NMdnGNdgkZ3bXlNUJFZDLdbg=
    $ curl icanhazip.com
    203.0.113.42

Copy the key and your IP address and head on over to the Draft `publishers`_
page, and click the ``WebHook URL`` link. Add your URL there, go to a draft
document and click the publish link. You should now see your blog posts when
you go http://localhost:8080.

.. _publishers: https://draftin.com/publishers

TODO:

Actually write some code. Also add more documentation for doing things like
changing up the templates.

.. .. _WebHooks: https://draftin.com/documents/69898?token=5fjKKlZ0-AeBzqj_RAftAGdzRzl9VBfBHj5wpSWm_gU)

.. * Free software: BSD license
.. * Documentation: http://draftin_a_flask.rtfd.org.

.. Usage
.. -----

.. ::

..     $ pip install draftin_a_flask
    $ env DIF_CONTENT=/path/to/content \
    DIF_OUTPUT=/path/to/output \
    DIF_PELICAN=/path/to/pelican_binary draftican
    Listening at endpoint QRFky1tR0KqHGM3cJoitwEi8tTpknaNnMpNHHiTIm8
    * Running on http://0.0.0.0:5678/
    * Restarting with reloader
    Listening at endpoint QRFky1tR0KqHGM3cJoitwEi8tTpknaNnMpNHHiTIm8
    
.. Setup your WebHook from within Draft, and now you can write your blog posts in
.. Draft and easily publish.


.. Future Features
.. ---------------

.. * Automatic uploads using rsync/ssh/file copy
.. * Settings provided in a file
.. * Improved error handling (e.g. missing title, etc.)


.. Known Bugs
.. ----------

.. * If you're missing important fields (like title and date) it probably will
..   skip publishing that doc.
