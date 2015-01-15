from datetime import datetime

from flask import render_template
from Forecast import Forecast

from app import app


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/zip/<zipcode>')
def forecastForZip(zipcode):
    return render_template("zip.html", forecast=Forecast(zipcode), time=datetime.now())
