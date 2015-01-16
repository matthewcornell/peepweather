from datetime import datetime

from flask import render_template
from Forecast import Forecast

from app import app


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/zip/<zipcode>')
def forecastForZip(zipcode):
    return render_template("forecast.html", forecast=Forecast(zipcode), time=datetime.now())


@app.route('/search/<query>')
def searchZip(query):
    return render_template("search.html", query=query, zipNameTuples=Forecast.searchZipcodes(query))
