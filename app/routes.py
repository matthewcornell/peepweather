from flask import render_template, request, redirect, url_for

from forecast.Hour import Hour
from forecast.Forecast import Forecast
from app import app


# ==== routes ====

@app.route('/')
def index():
    return render_template("index.html", colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/forecast/<zipOrLatLon>')
def showForecast(zipOrLatLon):
    """
    :param zipOrLatLon: location to get the forecast for. either a zip code string or a comma-separated list of
    latitude and longitude strings. ex: '01002' or '42.375370,-72.519249'
    Query parameters: Three comma-separated lists of integers, as returned by Forecast.urlQueryParamsForDefaultRanges().
    All three are always required for a forecast: precip_steps, temp_steps, wind_steps.
    :return:
    """
    try:
        # create zipcode arg
        if ',' in zipOrLatLon:
            zipOrLatLonList = zipOrLatLon.split(',')
        else:
            zipOrLatLonList = zipOrLatLon

        # create rangeDict arg
        rangeDict = Forecast.rangeDictFromUrlQueryParams(
            request.args.get('precip_steps'), request.args.get('temp_steps'), request.args.get('wind_steps'))

        # render the new Forecast!
        forecast = Forecast(zipOrLatLonList, rangeDict)
        return render_template("forecast.html", forecast=forecast,
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)
    except ValueError as ve:
        return render_template("forecast-error.html", error=ve.args[0],
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/search/<query>')
def searchForZip(query):
    return render_template("search.html", query=query, zipNameLatLonTuples=Forecast.searchZipcodes(query))


# ==== forms ====

@app.route('/submit_zip', methods=['POST'])
def do_zip_submit():
    zipVal = request.form.get('zip_form_value', None)
    # ex: http://127.0.0.1:5000/forecast/09003?precip_steps=10,30&temp_steps=32,41,70,85&wind_steps=8,12
    precipParam, tempParam, windParam = Forecast.urlQueryParamsForDefaultRanges()
    return redirect(url_for('showForecast', zipOrLatLon=zipVal,
                            precip_steps=precipParam, temp_steps=tempParam, wind_steps=windParam))


@app.route('/lat_lon_submit', methods=['POST'])
def do_lat_lon_submit():
    latVal = request.form.get('lat_form_value', None)
    lonVal = request.form.get('lon_form_value', None)
    return redirect(url_for('showForecast', zipOrLatLon=latVal + ',' + lonVal))


@app.route('/zip_search_submit', methods=['POST'])
def do_zip_search_submit():
    queryVal = request.form.get('query_form_value', None)
    return redirect(url_for('searchForZip', query=queryVal))
