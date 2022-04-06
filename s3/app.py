"""
SFU CMPT 756
Sample application---Checkout service.
"""

# Standard library modules
import logging
import sys
import time

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

import jwt

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Checkout process')

bp = Blueprint('app', __name__)

db = {
    "name": "http://cmpt756db:30002/api/v1/datastore",
    "endpoint": [
        "lend",
        "returnBook",
        "delete",
        "update"
    ]
}


@bp.route('/', methods=['GET'])
@metrics.do_not_track()
def hello_world():
    return ("If you are reading this in a browser, your service is "
            "operational. Switch to curl/Postman/etc to interact using the "
            "other HTTP verbs.")


@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route('/lend', methods=['POST'])
def lend_book():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        author = content['author']
        title = content['title']
        availability = content['availability']
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    if (availability == True):
        url = db['name'] + '/' + db['endpoint'][1]
        response = requests.post(url, json={"objtype": "Book", "author": author, "title": title, "availability": False },
        headers={'Authorization': headers['Authorization']})
        return (response.json())
    else:
        return json.dumps({"message": "Book is not currently available for lending"})


@bp.route('/returnBook', methods=['POST'])
def return_book():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        author = content['author']
        title = content['title']
    except Exception:
        return json.dumps({"message": "error reading arguments"})
        
    url = db['name'] + '/' + db['endpoint'][2]
    response = requests.post(url, json={"objtype": "Book", "author": author, "title": title, "availability": True },
    headers={'Authorization': headers['Authorization']})
    return (response.json())
	

# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix='/api/v1/checkout/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
