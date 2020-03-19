import csv
import datetime
from io import StringIO

from flask import Flask, Response

from covid_micro.app import plot, predictions, logger, get_cached, URL_TIMESERIES_CONFIRMED, \
    plot_doublingtime_estimates, plot_deathrate_vs_detection, plot_deaths_per_confirmed

__version__ = 0.1


def create_app():
    app = Flask(__name__)

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
<h1>{country}</h1><BR/>
<A HREF="index.html">list of countries</A>
<P><b>Doubling time:</b> {t2} Days<BR/>
<b>100k infections on</b> {date100k}<BR/>
<b>1M infections on</b> {date1m}<BR/>
<b>deaths/confirmed cases:</b> {deaths_per_confirmed}<BR/></P>
latest upstream has timestamp {timestamp}: <BR/><B>cases:</B> {cases}<BR/><B>deaths:</B> {deaths}<BR/>
<IMG SRC="{country}_timeseries.svg"><IMG SRC="{country}_doublingtime.svg">
<IMG SRC="{country}_deathrate_shifted.svg">
<IMG SRC="{country}_death_per_confirmed.svg">
<P><B>methodology:</B> To evaluate the current doubling time and make the predictions, a linear equation is fit against the logarithm of the five most recent (finished) days of the time
series data.<BR/>To evaluate the doubling time trend over time, the fit is repeated for chunks of five days.</P>

<P>Information on estimates using deaths: following <A HREF="https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca">this article</A>
it is assumed that people die on average on day 17.3 if they do. Some may die earlier so the plots are not accurate in that
respect -- I could not find a propability distribution for thime between infection and death anywhere.
<BR/>
Furthermore the minimum rates of deaths (good healthcare system, not overwhelmed ~ 0.8%) and maximum (overwhelmed healthcare system like in Wuhan and Italy, 3.5% were taken from that article.
The assumptions built on deaths are assuming that the disease has spread uninihbitetly. See for instance <a HREF="https://xn--grgen-jua.name/covid/Korea,%20South.html">South Korea</A> for an example where that assumption does not hold any more.
</P>

<P><B>Intensive care beds/capita</B>: Assuming all intensive care beds in a country are given to COVID-19 patients, and that
5%-10% of COVID-19 patients need intensive care, these lines indicate when the respective number of infected needing
intensive care exceeds the number ov available beds. Because the infection is not distributed isotropically, 
some areas of the country will see an overload of their hospitals way earlier, some others slightly later.
<B>Note that no matter how many beds you have on an exponential with typical doubling time of 3-5 days it buys you only a 
few days.</B>
Some reference countries have <A HREF=¨https://sccm.org/Blog/March-2020/United-States-Resource-Availability-for-COVID-19?_zs=jxpjd1&_zl=w9pb6">this many ICU beds</A> / 100k population.
Note that surely some of these are in use by non-COVID-patients so likely even the best health care systems won't have
30 beds/100k COVID patients<BR/>
<BR/><B>US: 34.7</B>
<BR/><B>Germany: 29.2</B>
<BR/><B>Italy: 12.5</B>
<BR/><B>France: 11.6</B>
<BR/><B>Spain: 9.7</B>
<BR/><B>UK: 6.6</B></P>

<P><b>deaths/confirmed cases:</b> a low number of deaths per confirmed case can be considered a good rate of testing or
a very early stage of the epidemic (because it takes some time for the diesease to kill people, so in the beginning
nobody is dead but there are already infected)..
A high number of deaths/detected case indicates either an overloaded health care system at least in sections
of a country or a low testing rate.</P>

<a href="https://github.com/gluap/covid_micro">Github repo</a>
</body>
</html>
"""
HTML_COUNTRIES = """
<html>
<title>List of Countries</title>
<Body>
<H1>List of countries</H1>
Caveat: Not all countries have enough data for a meaningful plot, but most larger developed nations sadly do.
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
