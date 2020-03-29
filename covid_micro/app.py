import csv
import datetime
import json
import logging
import pickle
from collections import namedtuple
from io import StringIO, BytesIO

WINDOW = 6

URL_TIMESERIES_CONFIRMED = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
URL_TIMESERIES_DEATHS = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
# URL_TIMESERIES_RECOVERED = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
URL_DAILY_REPORTS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{month:02d}-{day:02d}-2020.csv"

URL_ARCGIS_LATEST = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1/query?f=json&where=(Confirmed%20%3E%200)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Deaths%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&resultOffset=0&resultRecordCount=400&cacheHint=true"

logger = logging.getLogger(__name__)

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

matplotlib.use('Agg')

import matplotlib.pyplot
import numpy as np
import requests

TSTuple = namedtuple("TSTuple", ['country', 'confirmed', 'deaths'])


class TimestampFixer:
    def __init__(self):
        try:
            self.seen_data = pickle.load(open("timestamp_cache", "rb"))
        except:
            self.seen_data = {}

    def find_timestamp(self, data, timestamp):
        if data.country in self.seen_data:
            if self.seen_data[data.country]['data'] == data:
                return self.seen_data[data.country]['timestamp']
            else:
                self.seen_data[data.country] = {'data': data, 'timestamp': timestamp}
                self.dump()
                return timestamp
        else:
            self.seen_data[data.country] = {'data': data, 'timestamp': timestamp}
            self.dump()
            return timestamp

    def dump(self):
        try:
            pickle.dump(self.seen_data, open('timestamp_cache', "wb"))
        except:
            pass


tsfixer = TimestampFixer()


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
    global tsfixer
    jsondata = get_cached(URL_ARCGIS_LATEST).content
    latest = json.loads(jsondata)
    try:
        latest_data = [i for i in latest['features'] if
                       i['attributes']["Country_Region"] == country]
    except KeyError:
        return dict(deaths="Unknown (upstream api overloaded)", cases="Unknown (upstream aoi overloaded)",
                    recovered="Unknown (upstream api overloaded)", timestamp=datetime.datetime.now(), error=True)
    latest_sum = {}
    for entry in latest_data:
        for attribute, value in entry['attributes'].items():
            if attribute not in latest_sum and value is not None:
                latest_sum[attribute] = value
            elif attribute != "Last_Update" and value is not None:
                latest_sum[attribute] += value
            elif value is not None:
                latest_sum[attribute] = max(latest_sum[attribute], value)
            else:
                continue
    latest_data = latest_sum
    try:
        latest_timestamp = datetime.datetime.fromtimestamp(latest_data['Last_Update'] / 1000)
        latest_cases = latest_data['Confirmed']
        latest_deaths = latest_data['Deaths']
        latest_recovered = latest_data['Recovered']
        latest_error = False
    except KeyError:
        latest_timestamp = datetime.datetime.now()
        latest_cases = "Upstream API timestamp missing"
        latest_deaths = "Upstream API timestamp missing"
        latest_recovered = "Upstream API timestamp missing"
        latest_error = True
    #    latest_cases = latest_data['Confirmed']
    #    latest_deaths = latest_data['Deaths']
    #    latest_recovered = latest_data['Recovered']
    latest_timestamp = tsfixer.find_timestamp(TSTuple(country, latest_cases, latest_deaths), latest_timestamp)
    return dict(deaths=latest_deaths, cases=latest_cases, recovered=latest_recovered, timestamp=latest_timestamp,
                error=latest_error)


def predictions(country="Germany"):
    curve_fit, x, country_data, country_data_deaths, country_data_recovered = get_and_fit(country)

    def when(l):
        try:
            return (np.log(l) - curve_fit[1]) / curve_fit[0]
        except TypeError:
            return None

    def when_date(n):
        return (datetime.datetime.now() + datetime.timedelta(days=-when(n))).date()

    doublingrate = - round(np.log(2) / curve_fit[0], 2) if when(1) is not None else None
    doublingrate_direct = -np.log(2) / ( \
                np.log(country_data[-3] / country_data[-1]) / ((x[-1] - x[-3]).total_seconds() / 24. / 3600)) if when(
        1) is not None else None
    try:
        current = get_latest(country)
    except ExtraDataError:
        current = dict()
    current.update(dict(country=country, t2_direct=doublingrate_direct, t2=doublingrate, date10k=when_date(10000),
                        date100k=when_date(100000),
                        date1m=when_date(1000000),
                        deaths_per_confirmed=round(country_data_deaths[-1] / country_data[-1], 4)))
    return current


def get_and_fit(country):
    country_data_deaths, country_data_recovered, country_data, log_y_data, x, x_data = timeseries_data(country)
    try:
        curve_fit = np.ma.polyfit(x_data, log_y_data, 1)
    except TypeError:
        curve_fit = [None, None]
    return curve_fit, x, country_data, country_data_deaths, country_data_recovered


def exact_timeseries():
    day = datetime.date(year=2020, month=2, day=2)
    timeseries = {}
    while day < datetime.date.today():
        report = get_cached(URL_DAILY_REPORTS.format(day=day.day, month=day.month)).content
        data = [row for row in csv.reader(StringIO(report.decode("utf-8")))]
        for row in data[1:]:
            timestamp = datetime.datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S")
            country = row[1]
            province = row[0]
            confirmed = row[3]
            deaths = row[4]
            recovered = row[5]
            if (country, province) not in timeseries:
                timeseries[(country, province)] = {"recovered": {"t": [], "y": []}, "deaths": {"t": [], "y": []},
                                                   "confirmed": {"t": [], "y": []}}
            timeseries[(country, province)]['recovered']['t'].append(timestamp)
            timeseries[(country, province)]['deaths']['t'].append(timestamp)
            timeseries[(country, province)]['confirmed']['t'].append(timestamp)
            timeseries[(country, province)]['recovered']['y'].append(recovered)
            timeseries[(country, province)]['deaths']['y'].append(deaths)
            timeseries[(country, province)]['confirmed']['y'].append(confirmed)

        day += datetime.timedelta(days=1)
    return ("bla")


def timeseries_data(country):
    latest = get_latest(country)

    country_data_confirmed, data = get_timeseries_from_url(country, URL_TIMESERIES_CONFIRMED)
    #    country_data_recovered, data_recovered = get_timeseries_from_url(country, URL_TIMESERIES_RECOVERED)
    country_data_recovered = None
    country_data_deaths, data_deaths = get_timeseries_from_url(country, URL_TIMESERIES_DEATHS)
    added = 0
    if not latest["error"]:
        country_data_recovered = np.append(country_data_recovered, latest["recovered"])
        country_data_confirmed = np.append(country_data_confirmed, latest["cases"])
        country_data_deaths = np.append(country_data_deaths, latest["deaths"])
        addded = 1

    country_data_active = country_data_confirmed  # - country_data_deaths - country_data_recovered

    x = [datetime.datetime.strptime(d, '%m/%d/%y') + datetime.timedelta(days=1) for d in data[0][4:]]

    if not latest["error"]:
        x.append(latest["timestamp"])

    mask = np.array(country_data_active) < 10

    x_data = np.ma.array([(datetime.datetime.now() - a).total_seconds() / 3600. / 24. for a in x], mask=mask)[
             max(len(x) - WINDOW, 0):]
    log_y_data = np.log(np.ma.array(country_data_active, mask=mask))[max(len(x) - WINDOW, 0):]

    return country_data_deaths, country_data_recovered, country_data_active, log_y_data, x, x_data


def get_timeseries_from_url(country, url):
    r = get_cached(url).content
    data = [row for row in csv.reader(StringIO(r.decode("utf-8")))]
    #### old handling for US from back when they reported the valid data only on a county basis
    #    if country == "not_needed_any_more":
    #        all_country_data = [d[4:] for d in data if country in d and "," in d[0]]
    #        all_country_data_numeric = np.array([[int(d) for d in c] for c in all_country_data])
    #    else:
    all_country_data = [d[4:] for d in data if country in d]
    all_country_data_numeric = np.array([[int(d) for d in c] for c in all_country_data])
    country_data = np.sum(all_country_data_numeric, 0)
    return country_data, data


def sliding_window_fit(country):
    country_data_deaths, country_data_recovered, country_data, log_y_data, x, x_data = timeseries_data(country)
    times = []
    dates = []
    for i in range(0, len(x) - WINDOW + 1):
        x_data = np.ma.array([(a - datetime.datetime.now()).total_seconds() / 24.0 / 3600.0 for a in x])[i:i + WINDOW]
        log_y_data = np.log(np.ma.array(country_data))[i:i + WINDOW]
        if max(np.ma.array(country_data)[i:i + WINDOW]) < 50:
            continue
        curve_fit = np.ma.polyfit(x_data, log_y_data, 1)
        doublingrate = np.log(2) / curve_fit[0]
        times.append(doublingrate)
        dates.append(x[i + WINDOW - 1])
    return times, dates


def estimate_from_daily(country, steps=1):
    country_data_deaths, country_data_recovered, country_data, log_y_data, x, x_data = timeseries_data(country)
    x_new = []
    y_new = []
    for n in range(len(country_data) - steps):
        if min(country_data[n:n + steps]) < 20:
            continue
        t2 = -np.log(2) / (
                np.log(country_data[n] / country_data[n + steps]) / (
                (x[n + steps] - x[n]).total_seconds() / 24. / 3600))
        if np.abs(t2) < 90000:
            x_new.append(x[n + steps])
            y_new.append(t2)
    return y_new, x_new


def plot_doublingtime_estimates(country):
    times, dates = sliding_window_fit(country)
    steps_t2_direct = 2
    times3, dates3 = estimate_from_daily(country, steps=steps_t2_direct)

    # fig = matplotlib.pyplot.figure(figsize=(5, 5), dpi=300)
    fig, axes = matplotlib.pyplot.subplots(nrows=2, ncols=1, sharex=True, sharey=True, figsize=(5, 5), dpi=300)

    ax2 = axes[1]  # fig.add_subplot(212)
    ax = axes[0]  # fig.add_subplot(211)

    if len(times) > 2:
        ax.set_ylim(0, max(times) + 3)
        ax.plot(dates, times, "g.")
        ax2.plot(dates3, times3, "b.")

        ax.plot(dates[-1:], times[-1:], marker="+", color="black")
        ax2.plot(dates3[-1:], times3[-1:], marker="+", color="black")
        ax.plot(dates, times, "g-", label="from fit over 5 data points")
        ax2.plot(dates3, times3, "b-", label="$T_2=\\frac{\\mathrm{ln}(2)(t_1-t_0)}{\\mathrm{ln}(n_1/n_0)}$")
        matplotlib.pyplot.setp(ax2.get_xticklabels(), rotation=25, ha="right", rotation_mode="anchor")
        ax2.grid(True, which="major")
        ax2.grid(True, which="minor", linewidth=0.5)
        ax.grid(True, which="major")
        ax.grid(True, which="minor", linewidth=0.5)
        ax2.legend(loc=2)
        ax.legend(loc=2)

    else:
        ax.text(0, 1, "Not enough data")

        ax.set_ylim(0, 2)
        ax.set_xlim(0, 2)
    ax2.set_xlabel("date")
    ax2.set_ylabel(f"$T_2$ over {steps_t2_direct} days")
    ax.set_ylabel(f"$T_2$ over 5 days")

    bio = BytesIO()
    FigureCanvas(fig)
    fig.savefig(bio, format="svg")
    matplotlib.pyplot.close(fig)
    return bio.getvalue()


def plot_deathrate_vs_detection(country):
    country_data_deaths, country_data_recovered, country_data, log_y_data, x, x_data = timeseries_data(country)

    shifted_x = [d + datetime.timedelta(days=17.3) for d in x]

    # fig = matplotlib.pyplot.figure(figsize=(5, 5), dpi=300)
    fig = matplotlib.pyplot.figure(dpi=300)
    ax = fig.add_subplot()

    ax.plot(x, country_data_deaths, "b.")
    ax.plot(shifted_x, country_data * 0.008, "g.")
    ax.plot(shifted_x[-1:], country_data[-1:] * 0.008, marker="+", color="black")
    ax.plot(x, country_data_deaths, "b", label="actual fatalities")
    ax.plot(x[-1:], country_data_deaths[-1:], "b", marker="+", color="black")

    ax.plot(shifted_x, country_data * 0.008, "g-", label="korea style deaths (cases*0.008) shifted + 17.3 days")
    ax.plot(shifted_x, country_data * 0.035, "r-", label="wuhan-style deaths (cases*0.035) shifted + 17.3 days")
    ax.plot(shifted_x, country_data * 0.035, "r.")
    ax.plot(shifted_x[-1:], country_data[-1:] * 0.035, marker="+", color="black")

    ax.fill_between(shifted_x, country_data * 0.008, country_data * 0.035, alpha=0.5,
                    label="range of expected fatalities assuming 100% detection now")
    
    ax.set_ylim((1,1e5))

    matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=25, ha="right", rotation_mode="anchor")
    ax.grid(True, which="major")
    ax.grid(True, which="minor", linewidth=0.5)
    ax.grid(True, which="major")
    ax.grid(True, which="minor", linewidth=0.5)
    ax.legend(loc=2)

    ax.set_xlim((shifted_x[0], shifted_x[-1]))

    ax.set_yscale('log')

    ax.set_ylabel(f"Fatalities (blue line left of shaded area \n => current cases likely underreported)")

    bio = BytesIO()
    FigureCanvas(fig)
    fig.savefig(bio, format="svg")
    matplotlib.pyplot.close(fig)
    return bio.getvalue()


def plot_deaths_per_confirmed(country):
    country_data_deaths, country_data_recovered, country_data, log_y_data, x, x_data = timeseries_data(country)

    shifted_x = [d + datetime.timedelta(days=11.0) for d in x]

    # fig = matplotlib.pyplot.figure(figsize=(5, 5), dpi=300)
    fig = matplotlib.pyplot.figure(dpi=300)
    ax = fig.add_subplot()

    ax.plot(x, country_data_deaths / country_data, "b.", label="deaths/confirmed cases")

    ax.plot(x[-1:], country_data_deaths[-1:] / country_data[-1:], marker="+", color="black")
    matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=25, ha="right", rotation_mode="anchor")
    ax.grid(True, which="major")
    ax.grid(True, which="minor", linewidth=0.5)
    ax.grid(True, which="major")
    ax.grid(True, which="minor", linewidth=0.5)
    ax.legend(loc=2)

    ax.set_xlim((shifted_x[0], shifted_x[-1]))

    ax.set_ylabel(f"deaths / confirmed cases")

    bio = BytesIO()
    FigureCanvas(fig)
    fig.savefig(bio, format="svg")
    matplotlib.pyplot.close(fig)
    return bio.getvalue()


COUNTRY_MAPPING = dict(US="United States of America")


def get_inhabitants(country):
    if country in COUNTRY_MAPPING:
        country = COUNTRY_MAPPING[country]
    res = get_cached(f"https://restcountries.eu/rest/v2/name/{country}").json()
    try:
        if len(res) == 1:
            return int(res[0]["population"])
        else:
            for dataset in res:
                if dataset['name'] == country:
                    return int(dataset['population'])
            return None

    except:
        return None


def get_tld(country):
    if country in COUNTRY_MAPPING:
        country = COUNTRY_MAPPING[country]
    res = get_cached(f"https://restcountries.eu/rest/v2/name/{country}").json()
    try:
        if len(res) == 1:
            return res[0]["topLevelDomain"][0]
        else:
            for dataset in res:
                if dataset['name'] == country:
                    return dataset['topLevelDomain'][0]
            return None

    except:
        return None


def plot(country="Germany"):
    curve_fit, x, country_data, country_data_deaths, country_data_recovered = get_and_fit(country)

    inhabitants = get_inhabitants(country)

    def when(l): return (np.log(l) - curve_fit[1]) / curve_fit[0]

    #    fun = np.exp(curve_fit[1]) * np.exp(curve_fit[0] * x_data)

    d0 = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    d1 = datetime.datetime.combine(datetime.date(year=2020, day=25, month=2), datetime.datetime.min.time())

    prediction_x = x.copy()
    prediction_x = [d0 - datetime.timedelta(days=10), d0 + datetime.timedelta(days=10)]

    prediction_x_days = np.array([(datetime.datetime.now() - a).days + 0.5 for a in prediction_x])
    prediction_y = np.exp(curve_fit[1]) * np.exp(curve_fit[0] * prediction_x_days)

    fig = matplotlib.pyplot.figure(dpi=300)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_yscale('log')

    ax.plot(x, country_data, "b.", label="actual detected cases")
    ax.plot(x[-1:], country_data[-1:], marker="+", color="black")
    ax.grid(True, which="major")
    ax.grid(True, which="minor", linewidth=0.5)

    ax.set_ylim((18, 1e3 * max(country_data_deaths / 0.008 * 2 ** (17.3 / 2))))
    #  ax.set_xlim((d1, d0 + datetime.timedelta(days=10)))
    ax.plot(prediction_x, prediction_y, "b-", label="fit")
    ax.plot(x, country_data_deaths / 0.008 * 2 ** (17.3 / 5), "g.", label="estimate from deaths $T_2= 5$ days, p=0.8%")
    ax.plot(x, country_data_deaths / 0.008 * 2 ** (17.3 / 2), "r.", label="estimate from deaths $T_2= 2$ days, p=0.8%")

    ax.plot(x[-1:], country_data_deaths[-1:] / 0.008 * 2 ** (17.3 / 5), marker="+", color="black")
    ax.plot(x[-1:], country_data_deaths[-1:] / 0.008 * 2 ** (17.3 / 2), marker="+", color="black")

    if inhabitants is not None:
        ax.axhline(10 * inhabitants / 100000 / 0.10, color="red", alpha=0.5)
        ax.axhline(30 * inhabitants / 100000 / 0.05, color="green", alpha=0.5)
        ax.text(x[0], 30 * inhabitants / 100000 / 0.05, "30 COVID-ICU beds/100k 5% need them", color="green",
                va="bottom")
        ax.text(x[0], 10 * inhabitants / 100000 / 0.05, "10 COVID-ICU beds/100k 10% need them", color="red",
                va="top")

    matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=25, ha="right",
                           rotation_mode="anchor")
    ax.set_xlabel("date")
    ax.set_ylabel(f"COVID-19 infections")

    ax.legend(loc=2)

    bio = BytesIO()
    FigureCanvas(fig)
    fig.savefig(bio, format="svg")
    matplotlib.pyplot.close(fig)
    return bio.getvalue()
