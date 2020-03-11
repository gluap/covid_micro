import csv
import datetime
from io import StringIO

from flask import Flask, Response

from covid_micro.app import plot, HTML_COUNTRIES, predictions, logger, ERROR, HTML, get_cached, URL_TIMESERIES_CSV

__version__ = 0.1


def create_app():
    app = Flask(__name__)

    @app.route('/<country>.svg')
    def deliver_plot(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[country] = {'data': plot(country),
                              'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/')
    @app.route('/index.html')
    def index():
        r = get_cached(URL_TIMESERIES_CSV).content
        data = [row for row in csv.reader(StringIO(r.decode("utf-8")))]
        countries = set([row[1] for row in data])
        return Response(
            HTML_COUNTRIES.format(countries="<LI>".join([f'<a href="{c}.html">{c}</a>' for c in sorted(countries)])))

    @app.route('/<country>.html')
    def html(country="Germany"):
        try:
            data = predictions(country)
        except Exception as exc:
            logger.exception("exception when making html")
            return Response(ERROR.format(country=country, exception=exc), mimetype="text/html")
        return Response(HTML.format(**data), mimetype='text/html')

    return app
