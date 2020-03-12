import csv
import datetime
import json
import logging
from io import StringIO, BytesIO

URL_TIMESERIES_CSV = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
URL_ARCGIS_LATEST = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1/query?f=json&where=(Confirmed%20%3E%200)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Deaths%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&resultOffset=0&resultRecordCount=400&cacheHint=true"

logger = logging.getLogger(__name__)

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

matplotlib.use('Agg')

import matplotlib.pyplot
import numpy as np
import requests


class ExtraDataError(Exception):
    pass


def get_cached(url, cache={}):
    if url in cache:
        if datetime.datetime.now() - cache[url]['timestamp'] <= datetime.timedelta(minutes=15):
            return cache[url]['data']
    result = requests.get(url)
    result_valid = True
    try:
        if "json" in result.url:
            data = json.loads(result.content)
            if 'error' in data:
                result_valid = False
    except:
        pass
    if result_valid:
        cache[url] = {'data': result,
                      'timestamp': datetime.datetime.now()}

    return result


def get_latest(country):
    jsondata = get_cached(URL_ARCGIS_LATEST).content
    latest = json.loads(jsondata)
    try:
        latest_data = [i for i in latest['features'] if
                       i['attributes']["Country_Region"] == country]
    except KeyError:
        return dict(deaths="Unknown (upstream api overloaded)", cases="Unknown (upstream aoi overloaded)",
                    recovered="Unknown (upstream api overloaded)", timestamp=datetime.datetime.now())
    latest_sum = {}
    for entry in latest_data:
        for attribute, value in entry['attributes'].items():
            if attribute not in latest_sum:
                latest_sum[attribute] = value
            elif attribute != "Last_Update":
                latest_sum[attribute] += value
            else:
                latest_sum[attribute] = max(latest_sum[attribute], value)
    latest_data = latest_sum
    try:
        latest_timestamp = datetime.datetime.fromtimestamp(latest_data['Last_Update'] / 1000)
        latest_cases = latest_data['Confirmed']
        latest_deaths = latest_data['Deaths']
        latest_recovered = latest_data['Recovered']
    except KeyError:
        latest_timestamp = datetime.datetime.now()
        latest_cases = "Upstream API timestamp missing"
        latest_deaths = "Upstream API timestamp missing"
        latest_recovered = "Upstream API timestamp missing"
    #    latest_cases = latest_data['Confirmed']
    #    latest_deaths = latest_data['Deaths']
    #    latest_recovered = latest_data['Recovered']
    return dict(deaths=latest_deaths, cases=latest_cases, recovered=latest_recovered, timestamp=latest_timestamp)


def predictions(country="Germany"):
    curve_fit, x, country_data = get_and_fit(country)

    def when(l):
        try:
            return (np.log(l) - curve_fit[1]) / curve_fit[0]
        except TypeError:
            return None

    def when_date(n):
        return (datetime.datetime.now() + datetime.timedelta(days=-when(n))).date()

    def howmany(d):
        return np.exp(curve_fit[1]) * np.exp(curve_fit[0] * d)

    doublingrate = round(-when(2) + when(1), 2) if when(1) is not None else None
    try:
        current = get_latest(country)
    except ExtraDataError:
        current = dict()
    current.update(dict(country=country, t2=doublingrate, date10k=when_date(10000), date100k=when_date(100000),
                        date1m=when_date(1000000)))
    return current


def get_and_fit(country):
    r = get_cached(URL_TIMESERIES_CSV).content
    data = [row for row in csv.reader(StringIO(r.decode("utf-8")))]
    if country=="US":
        all_country_data = [d[4:] for d in data if country in d and "," in d[0]]
        all_country_data_numeric = np.array([[int(d) for d in c] for c in all_country_data])
    else:
        all_country_data = [d[4:] for d in data if country in d]
        all_country_data_numeric = np.array([[int(d) for d in c] for c in all_country_data])
    country_data = np.sum(all_country_data_numeric, 0)
    x = [datetime.datetime.strptime(d, '%m/%d/%y') + datetime.timedelta(days=1) for d in
         data[0][-len(country_data) + len(data[0]):]]
    mask = np.array(country_data) < 20
    x_data = np.ma.array([(datetime.datetime.now() - a).days for a in x], mask=mask)[max(len(x) - 6, 0):]
    log_y_data = np.log(np.ma.array(country_data, mask=mask))[max(len(x) - 6, 0):]
    try:
        curve_fit = np.ma.polyfit(x_data, log_y_data, 1)
    except TypeError:
        curve_fit = [None, None]
    return curve_fit, x, country_data


def plot(country="Germany"):
    curve_fit, x, country_data = get_and_fit(country)

    def when(l): return (np.log(l) - curve_fit[1]) / curve_fit[0]

    #    fun = np.exp(curve_fit[1]) * np.exp(curve_fit[0] * x_data)

    d0 = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    d1 = datetime.datetime.combine(datetime.date(year=2020, day=25, month=2), datetime.datetime.min.time())

    prediction_x = x.copy()
    prediction_x.append(d0 + datetime.timedelta(days=10))

    prediction_x_days = np.array([(datetime.datetime.now() - a).days for a in prediction_x])
    prediction_y = np.exp(curve_fit[1]) * np.exp(curve_fit[0] * prediction_x_days)

    fig = matplotlib.pyplot.figure(figsize=(5, 5), dpi=300)
    ax = fig.add_subplot(2, 1, 1)
    ax.set_yscale('log')

    ax.plot(x, country_data, "g.")

    ax.grid(True, which="major")
    ax.grid(True, which="minor", linewidth=0.5)

    ax.set_ylim((18, 5e5))
    #  ax.set_xlim((d1, d0 + datetime.timedelta(days=10)))
    ax.plot(prediction_x, prediction_y, "b-")

    matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=45, ha="right",
                           rotation_mode="anchor")
    ax.set_xlabel("date")
    ax.set_ylabel(f"COVID-19 infections")
    ax.set_title(country)

    latest = get_latest(country)
    ax.plot([latest['timestamp']], [latest['cases']], 'g.')
    bio = BytesIO()
    FigureCanvas(fig)
    fig.savefig(bio, format="svg")
    matplotlib.pyplot.close(fig)
    return bio.getvalue()
