from datetime import datetime

from flask import render_template, request

from forecast.Hour import Hour
from forecast.Forecast import Forecast
from app import app


@app.route('/')
def index():
    return render_template("index.html", colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/forecast/<zipcode>')
def forecastForZip(zipcode):
    """
    :param zipcode: zipcode to show the forecast for. the 'format' parameter is optional and can be either 'calendar'
    (the default) or 'list
    :return:
    """
    formatType = request.args.get('format', 'calendar')  # to access parameters submitted in the URL (?key=value)
    forecast = Forecast(zipcode)
    if forecast.error:
        return render_template("forecast-error.html", forecast=forecast, time=datetime.now(),
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)
    elif formatType == 'list':
        return render_template("forecast-list.html", forecast=forecast, time=datetime.now(),
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)
    elif formatType == 'calendar':
        return render_template("forecast-calendar.html", forecast=forecast, time=datetime.now(),
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)
    else:
        return "invalid format type. must be either 'calendar' or 'list'"  # TODO


@app.route('/search/<query>')
def searchZip(query):
    return render_template("search.html", query=query, zipNameLatLonTuples=Forecast.searchZipcodes(query))
