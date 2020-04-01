import pytest
import datetime
from covid_micro import app

countries = ["Germany", "US", "France", "Italy", "Korea, South"]


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_stats(country):
    a = app.get_latest(country)
    assert isinstance(a['deaths'], int)
    assert isinstance(a['timestamp'], datetime.datetime)


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_predictions(country):
    p = app.predictions(country)
    assert not p['error']
    assert isinstance(p['t2'], float)


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_get_and_fit(country):
    gf = app.get_and_fit(country)
    print(gf)


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_get_and_fit(country):
    gf = app.timeseries_data(country)
    assert gf[0][-1] > 0
    assert gf[2][-1] > 0


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_sliding_fit(country):
    gf = app.sliding_window_fit(country)
    assert isinstance(gf[1][0], datetime.datetime)
    assert gf[0][-1] > 0


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_estimate_from_daily(country):
    gf = app.estimate_from_daily(country)
    assert isinstance(gf[1][0], datetime.datetime)
    assert gf[0][-1] > 0


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_plots(country):
    p1 = app.plot(country)
    p2 = app.plot_deathrate_vs_detection(country)
    p3 = app.plot_doublingtime_estimates(country)
    p4 = app.plot_deaths_per_confirmed(country)
    p5 = app.plot_daily_infected(country)

    assert p1.startswith(b"<?xml version")
    assert p2.startswith(b"<?xml version")
    assert p3.startswith(b"<?xml version")
    assert p4.startswith(b"<?xml version")
    assert p5.startswith(b"<?xml version")



def test_get_tld():
    de = app.get_tld("Germany")
    assert de == de
