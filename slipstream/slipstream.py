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

from flask import Flask, abort
from . import util

app = Flask(__name__)
app.config['API_KEY'] = util.get_api_key()


@app.route('/<api_key>', methods=['POST'])
def api(api_key):
    if api_key != app.config['API_KEY']:
        abort(403)
    return 'OK'
