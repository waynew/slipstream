'''
Copyright 2015 - Wayne Werner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json
import os
from flask import Flask, abort, request, send_from_directory
from . import util
from . import core
from . import config

app = Flask(__name__)
app.config['API_KEY'] = util.get_api_key()


@app.route('/<api_key>', methods=['POST'])
def api(api_key):
    if api_key != app.config['API_KEY']:
        app.logger.warning('Bad API key %r', api_key)
        abort(403)
    else:
        app.logger.info('hi')
        app.logger.info('Payload: %s', request.form['payload'])
        payload = json.loads(request.form['payload'])
        # TODO: Also pass created/updated dates -W. Werner, 2015-11-21
        core.publish(id=payload['id'],
                     title=payload['name'],
                     content=payload['content'],
                     author=payload['user']['email'],
                     )

        app.logger.debug(payload)
        return 'OK'


@app.route('/preview', defaults={'path': 'index.html'})
@app.route('/preview/<path:path>')
def preview(path):
    core.env = core.jinja2.Environment(
        loader = core.jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                                      'themes'))
    )
    core.env.globals.update(app.config)
    core.regenerate(content_dir=app.config['CONTENT_DIR'],
                    output_dir=app.config['OUTPUT_DIR'],
                    )
    app.logger.debug(app.config['OUTPUT_DIR'])
    return send_from_directory(app.config['OUTPUT_DIR'], path)


def run():
    app.config['CONTENT_DIR'] = os.path.abspath(
        os.environ.get('SLIPSTREAM_CONTENT_DIR', 'content')
    )
    app.config['OUTPUT_DIR'] = os.path.abspath(
        os.environ.get('SLIPSTREAM_OUTPUT_DIR', 'output')
    )
    app.config['DEFAULT_AUTHOR'] = os.environ.get('SLIPSTREAM_DEFAULT_AUTHOR',
                                                  'Anonymous')
    app.config['POST_TEMPLATE'] = core.env.get_template(
        os.environ.get('SLIPSTREAM_POST_TEMPLATE', 'post.html')
    )
    app.config['SITE_URL'] = os.environ.get('SLIPSTREAM_SITE_URL', '')
    app.config['BLOG_NAME'] = os.environ.get('SLIPSTREAM_BLOG_NAME')
    app.logger.debug('Site url: %r', app.config['SITE_URL'])
    ip = os.environ.get('SLIPSTREAM_IP_ADDR', '0.0.0.0')
    port = int(os.environ.get('SLIPSTREAM_PORT', 5000))
    debug = str(os.environ.get('SLIPSTREAM_DEBUG')).lower() == 'true'
    config.update(app.config)
    core.env.globals.update(app.config)
    core.regenerate(content_dir=app.config['CONTENT_DIR'],
                    output_dir=app.config['OUTPUT_DIR'])
    app.run(ip, port=port, debug=debug)
