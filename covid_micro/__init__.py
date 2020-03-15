import csv
import datetime
from io import StringIO

from flask import Flask, Response

from covid_micro.app import plot, predictions, logger, get_cached, URL_TIMESERIES_CONFIRMED, \
    plot_doublingtime_estimates, plot_deathrate_vs_detection

__version__ = 0.1


def create_app():
    app = Flask(__name__)

    @app.route('/<country>_timeseries.svg')
    def deliver_plot(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[country] = {'data': plot(country),
                              'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/<country>_doublingtime.svg')
    def deliver_plot_doublingtimes(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[country] = {'data': plot_doublingtime_estimates(country),
                              'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/<country>_deathrate_shifted.svg')
    def deliver_plot_deathrates(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[country] = {'data': (plot_deathrate_vs_detection(country)),
                              'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/')
    @app.route('/index.html')
    def index():
        r = get_cached(URL_TIMESERIES_CONFIRMED).content
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


HTML = """
<html>
<title>Current {country} corona statistics</title> 
<body>
<h1>{country}</h1>
<P><b>Doubling time:</b> {t2} Days<BR/>
<b>10k infections on</b> {date10k}<BR/>
<b>100k infections on</b> {date100k}<BR/>
<b>1M infections on</b> {date1m}<BR/></P>
latest upstream has timestamp {timestamp}: <BR/><B>cases:</B> {cases}<BR/><B>deaths:</B> {deaths}<BR/>
<IMG SRC="{country}_timeseries.svg"><IMG SRC="{country}_doublingtime.svg">
<IMG SRC="{country}_deathrate_shifted.svg">

<P><B>methodology:</B> To evaluate the current doubling time and make the predictions, a linear equation is fit against the logarithm of the five most recent (finished) days of the time
series data.<BR/>To evaluate the doubling time trend over time, the fit is repeated for chunks of five days.</P>
<BR/>
<a href="https://github.com/gluap/covid_micro">Github repo</a>
</body>
</html>
"""
HTML_COUNTRIES = """
<html>
<title>List of Countries</title>
<Body>
<ul>
<LI/>{countries}
</ul>
</body>
</html
"""
ERROR = """
<html>
<title>error fetching {country}</title>
<Body>
There was a problem fetching {country}. {exception}
</body>
</html>"""
