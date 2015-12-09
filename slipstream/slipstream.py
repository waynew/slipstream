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
        payload = json.loads(request.form['payload'])
        # TODO: Also pass created/updated dates -W. Werner, 2015-11-21
        core.publish(id=payload['id'],
                     title=payload['name'],
                     content=payload['content'],
                     author=payload['user']['email'],
                     )

        app.logger.debug(payload)
        return 'OK'


@app.route('/preview/<path:path>')
def preview(path):
    return send_from_directory('/tmp/fnord/', path)


def run():
    app.run('0.0.0.0', debug=True)
