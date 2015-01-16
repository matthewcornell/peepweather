from datetime import datetime

from flask import render_template, request

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
    if formatType == 'list':
        return render_template("forecast.html", forecast=Forecast(zipcode), time=datetime.now())
    elif formatType == 'calendar':
        return "calendar format type unimplemented"     # TODO
    else:
        return "invalid format type. must be either 'calendar' or 'list'"   # TODO


@app.route('/search/<query>')
def searchZip(query):
    return render_template("search.html", query=query, zipNameTuples=Forecast.searchZipcodes(query))
