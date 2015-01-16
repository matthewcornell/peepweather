from datetime import datetime

from flask import render_template, request
from forecast.Hour import Hour

from forecast.Forecast import Forecast
from app import app


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/forecast/<zipcode>')
def forecastForZip(zipcode):
    """
    :param zipcode: zipcode to show the forecast for. the 'format' parameter is optional and can be either 'calendar'
    (the default) or 'list
    :return:
    """
    formatType = request.args.get('format', 'list')    # to access parameters submitted in the URL (?key=value). TODO change to 'calendar' when implemented
    forecast = Forecast(zipcode)
    if forecast.error:
        return render_template("forecast-error.html", forecast=forecast, time=datetime.now())
    elif formatType == 'list':
        return render_template("forecast-list.html", forecast=forecast, time=datetime.now())
    elif formatType == 'calendar':
        return render_template("forecast-calendar.html", forecast=forecast, time=datetime.now(),
                               HOUR_OF_DAY_RANGE=Hour.HOUR_OF_DAY_RANGE, DAY_OF_WEEK_RANGE=Hour.DAY_OF_WEEK_RANGE)
    else:
        return "invalid format type. must be either 'calendar' or 'list'"   # TODO


@app.route('/search/<query>')
def searchZip(query):
    return render_template("search.html", query=query, zipNameTuples=Forecast.searchZipcodes(query))
