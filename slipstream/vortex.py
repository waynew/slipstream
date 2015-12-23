import os

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from . import slipstream
from . import core
from . import config

def run():
    slipstream.app.config['CONTENT_DIR'] = os.path.abspath(
        os.environ.get('SLIPSTREAM_CONTENT_DIR', 'content')
    )
    slipstream.app.config['OUTPUT_DIR'] = os.path.abspath(
        os.environ.get('SLIPSTREAM_OUTPUT_DIR', 'output')
    )
    slipstream.app.config['DEFAULT_AUTHOR'] = os.environ.get('SLIPSTREAM_DEFAULT_AUTHOR',
                                                  'Anonymous')
    slipstream.app.config['POST_TEMPLATE'] = core.env.get_template(
        os.environ.get('SLIPSTREAM_POST_TEMPLATE', 'post.html')
    )
    slipstream.app.config['SITE_URL'] = os.environ.get('SLIPSTREAM_SITE_URL', '')
    slipstream.app.config['BLOG_NAME'] = os.environ.get('SLIPSTREAM_BLOG_NAME')
    slipstream.app.logger.debug('Site url: %r', slipstream.app.config['SITE_URL'])
    ip = os.environ.get('SLIPSTREAM_IP_ADDR', '0.0.0.0')
    port = int(os.environ.get('SLIPSTREAM_PORT', 5000))
    debug = str(os.environ.get('SLIPSTREAM_DEBUG')).lower() == 'true'
    config.update(slipstream.app.config)
    core.env.globals.update(slipstream.app.config)
    core.regenerate(content_dir=slipstream.app.config['CONTENT_DIR'],
                    output_dir=slipstream.app.config['OUTPUT_DIR'])

    http_server = HTTPServer(WSGIContainer(slipstream.app))
    http_server.listen(port)
    IOLoop.instance().start()


if __name__ == '__main__':
    run()
