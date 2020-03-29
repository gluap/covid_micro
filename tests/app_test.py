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
    assert isinstance(p['t2'],float)


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_get_and_fit(country):
    gf = app.get_and_fit(country)
    print(gf)


@pytest.mark.parametrize("country", countries)
@pytest.mark.vcr()
def test_get_and_fit(country):
    gf = app.timeseries_data(country)
    assert gf[0][-1]>0
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