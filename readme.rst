covid_micro
===========
.. image:: https://travis-ci.org/gluap/pyduofern.svg?branch=master
    :target: https://travis-ci.org/gluap/covid_micro
.. image:: https://coveralls.io/repos/github/gluap/pyduofern/badge.svg?branch=master
    :target: https://coveralls.io/github/gluap/covid_micro?branch=master
quickly hacked python based web service to plot corona virus case numbers.

Fits an exponential to find doubling time etc...

Uses data provided by John Hopkins university (https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6 / https://github.com/CSSEGISandData/2019-nCoV)

usage::
    
    export FLASK_APP=covid_micro.app
    flask run

