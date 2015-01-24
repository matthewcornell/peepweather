from flask import render_template, request, redirect, url_for

from forecast.Hour import Hour
from forecast.Forecast import Forecast
from app import app


@app.route('/')
def index():
    return render_template("index.html", colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/forecast/<zipOrLatLon>')
def showForecast(zipOrLatLon):
    """
    :param zipOrLatLon: location to get the forecast for. either a zip code string or a comma-separated list of
    latitude and longitude strings. ex: '01002' or '42.375370,-72.519249'
    :return:
    """
    try:
        if ',' in zipOrLatLon:
            zipOrLatLonList = zipOrLatLon.split(',')
        else:
            zipOrLatLonList = zipOrLatLon
        forecast = Forecast(zipOrLatLonList, Forecast.defaultRangeDict())
        return render_template("forecast.html", forecast=forecast,
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)
    except ValueError as ve:
        return render_template("forecast-error.html", error=ve.args[0],
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/search/<query>')
def searchForZip(query):
    return render_template("search.html", query=query, zipNameLatLonTuples=Forecast.searchZipcodes(query))


#
# forms
#

@app.route('/doZipSubmit', methods=['POST'])
def doZipSubmit():
    zipVal = request.form.get('zip_form_value', None)
    return redirect(url_for('showForecast', zipOrLatLon=zipVal))


@app.route('/doLatLonSubmit', methods=['POST'])
def doLatLonSubmit():
    latVal = request.form.get('lat_form_value', None)
    lonVal = request.form.get('lon_form_value', None)
    return redirect(url_for('showForecast', zipOrLatLon=latVal + ',' + lonVal))


@app.route('/doZipSearchSubmit', methods=['POST'])
def doZipSearchSubmit():
    queryVal = request.form.get('query_form_value', None)
    return redirect(url_for('searchForZip', query=queryVal))
