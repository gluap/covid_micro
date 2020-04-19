import csv
import datetime
import os.path
from io import StringIO

from flask import Flask, Response
from flask_apscheduler import APScheduler
from jinja2 import Environment, PackageLoader, select_autoescape

from covid_micro.app import plot, predictions, logger, get_cached, URL_TIMESERIES_CONFIRMED, \
    plot_doublingtime_estimates, plot_deathrate_vs_detection, plot_deaths_per_confirmed, load_countries, \
    plot_daily_infected, rich_country_list
from covid_micro.germany import plot_kreis, get_data_by_name, number_by_name

env = Environment(
    loader=PackageLoader('covid_micro', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def create_app():
    app = Flask(__name__)

    class Config(object):
        SCHEDULER_API_ENABLED = True
        JOBS = [
            {
                'id': 'load_countries',
                'func': load_countries,
                'trigger': 'interval',
                'seconds': 900
            }
        ]

    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    @app.route('/<country>_timeseries.svg')
    def deliver_plot(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            try:
                cache[country] = {'data': plot(country),
                                  'timestamp': datetime.datetime.now()}
            except (TypeError, ValueError):
                cache[country] = {'data': plot(country),
                                  'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/favicon.png')
    def deliver():
        return Response(open(os.path.join(os.path.dirname(__file__), "favicon.png"), "rb").read(), mimetype="image/png")

    @app.route('/<country>_doublingtime.svg')
    def deliver_plot_doublingtimes(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            try:
                cache[country] = {'data': plot_doublingtime_estimates(country),
                                  'timestamp': datetime.datetime.now()}
            except (TypeError, ValueError):
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

    @app.route('/<country>_death_per_confirmed.svg')
    def deliver_plot_death_per_confirmed(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[country] = {'data': (plot_deaths_per_confirmed(country)),
                              'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/<country>_daily_infected.svg')
    def deliver_daily_infected(country="Germany", cache={}):
        if country not in cache or (
                datetime.datetime.now() - cache[country]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[country] = {'data': (plot_daily_infected(country)),
                              'timestamp': datetime.datetime.now()}
        return Response(cache[country]['data'], mimetype='image/svg+xml')

    @app.route('/')
    @app.route('/index_old.html')
    def index():
        r = get_cached(URL_TIMESERIES_CONFIRMED).content
        data = [row for row in csv.reader(StringIO(r.decode("utf-8")))]
        countries = set([row[1] for row in data])
        return Response(
            HTML_COUNTRIES.format(countries="<LI>".join([f'<a href="{c}">{c}</a>' for c in sorted(countries)])))

    @app.route('/index.html')
    def index2(cache={}):
        if 'last' not in cache or (cache['last'] - datetime.datetime.now()) > datetime.timedelta(hours=4):
            data = rich_country_list()
            template = env.get_or_select_template("index.jinja")
            cache['data']=template.render({'countries': data, "title": "list of countries"})
            cache['last']=datetime.datetime.now()
        return Response(cache['data'])

    @app.route('/<country>.html')
    @app.route('/countries/<country>')
    def html(country="Germany"):
        try:
            data = predictions(country)
        except Exception as exc:
            logger.exception("exception when making html")
            return Response(ERROR.format(country=country, exception=exc), mimetype="text/html")
        template = env.get_or_select_template("country.jinja")
        return Response(template.render({**data, "title": f"{country} corona statistics"}), mimetype='text/html')

    @app.route('/de/<kreis>.svg')
    def plotout_kreis(kreis="Darmstadt", cache={}):
        if kreis not in cache or (
                datetime.datetime.now() - cache[kreis]['timestamp'] > datetime.timedelta(minutes=15)):
            cache[kreis] = {'data': (plot_kreis(kreis)),
                            'timestamp': datetime.datetime.now()}
        return Response(cache[kreis]['data'], mimetype='image/svg+xml')

    @app.route('/de/<kreis>')
    def html_kreis(kreis="Darmstadt"):
        try:
            raw_data = get_data_by_name(kreis)
            data = {'kreis': kreis, **raw_data[2]['currentStats'], **raw_data[0]}
        except Exception as exc:
            logger.exception("exception when making html")
            return Response(ERROR.format(country=kreis, exception=exc), mimetype="text/html")
        return Response(HTML_KREIS.format(**data), mimetype='text/html')

    @app.route('/de/')
    @app.route('/de/index.html')
    def index_de():
        kreise = number_by_name.keys()

        return Response(
            HTML_KREISE.format(kreise="<LI>".join([f'<a href="{c}">{c}</a>' for c in sorted(kreise)])))

    return app


HTML_COUNTRIES = """
<html>
<head profile="http://www.w3.org/2005/10/profile">
<link rel="icon" 
      type="image/png" 
      href="favicon.png">

<title>List of Countries</title>
</head><Body>
<H1>List of countries</H1>
Caveat: Not all countries have enough data for a meaningful plot, but most larger developed nations sadly do.
<ul>
<LI/>{countries}
</ul>
</body>
</html>
"""
ERROR = """
<html>
<head profile="http://www.w3.org/2005/10/profile">
<link rel="icon" 
      type="image/png" 
      href="favicon.png"> 
<title>error fetching {country}</title>
</head>
<Body>
There was a problem fetching {country}. {exception}
</body>
</html>"""

HTML_KREISE = """
<HTML>
<head profile="http://www.w3.org/2005/10/profile">
<link rel="icon" 
      type="image/png" 
      href="favicon.png">

<title>Landkreise</title>
</head><Body>
<ul>
<LI/>{kreise}
</ul>
</body>
</html>
"""

HTML_KREIS = """
<HTML>
<head profile="http://www.w3.org/2005/10/profile">
<link rel="icon" 
      type="image/png" 
      href="favicon.png">

<title>{kreis}</title>
</head><Body>
<H1>{kreis}</h1>
<B>Bundesland:</B> {bundesland}
<B>Einwohner:</B> {population}
<B>Fälle:</B> {count}
<B>davon genesen:</B> {recovered}
<B>verstorben:</B> {dead}
<B>active:</B> {active}<BR/>
<IMG style="vertical-align:top" SRC="{kreis}.svg"><BR/>
<B>Quelle:</B> Die ZEIT.<BR/>
Da Genesungen nicht Meldepflichtig sind, werden diese teilweise gar nicht, oft auch nicht jeden Tag
erfasst, was dazu führt, dass teilweise die Darstellung der kumulativen genesenen Fälle sehr stufig daher kommt.
</body>
</html>
"""
