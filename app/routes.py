from flask import render_template, request, redirect, url_for

from forecast.Hour import Hour
from forecast.Forecast import Forecast
from app import app


@app.route('/')
def index():
    return render_template("index.html", colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/forecast/<zipOrLatLon>')
def forecastForLocation(zipOrLatLon):
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
        forecast = Forecast(zipOrLatLonList)
        return render_template("forecast.html", forecast=forecast,
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)
    except ValueError as ve:
        return render_template("forecast-error.html", error=ve.args[0],
                               colorKeyHighToLow=Hour.COLOR_SEQ_HIGH_TO_LOW)


@app.route('/search/<query>')
def searchForZip(query):
    return render_template("search.html", query=query, zipNameLatLonTuples=Forecast.searchZipcodes(query))


@app.route('/parameters/')
def editParameters():
    precipVals = Hour.PARAM_RANGE_STEPS['precip']
    windVals = Hour.PARAM_RANGE_STEPS['wind']
    tempVals = Hour.PARAM_RANGE_STEPS['temp']
    return render_template("parameter-edit.html", precipVals=precipVals, windVals=windVals, tempVals=tempVals)


#
# forms
#

@app.route('/doZipSubmit', methods=['POST'])
def doZipSubmit():
    zipVal = request.form.get('zip_form_value', None)
    return redirect(url_for('forecastForLocation', zipOrLatLon=zipVal))


@app.route('/doLatLonSubmit', methods=['POST'])
def doLatLonSubmit():
    latVal = request.form.get('lat_form_value', None)
    lonVal = request.form.get('lon_form_value', None)
    return redirect(url_for('forecastForLocation', zipOrLatLon=latVal + ',' + lonVal))


@app.route('/doEditParametersSubmit', methods=['POST'])
def doEditParametersSubmit():
    windV1Val = request.form.get('wind-v1-value', None)
    windV2Val = request.form.get('wind-v2-value', None)
    precipV1Val = request.form.get('precip-v1-value', None)
    precipV2Val = request.form.get('precip-v2-value', None)
    tempV1Val = request.form.get('temp-v1-value', None)
    tempV2Val = request.form.get('temp-v2-value', None)
    tempV3Val = request.form.get('temp-v3-value', None)
    tempV4Val = request.form.get('temp-v4-value', None)
    try:
        paramRangeSteps = {'precip': (int(precipV1Val), int(precipV2Val)),  # H-M-L
                           'wind': (int(windV1Val), int(windV2Val)),  # H-M-L
                           'temp': (int(tempV1Val), int(tempV2Val), int(tempV3Val), int(tempV4Val))}  # L-M-H-M-L
    except ValueError:
        # TODO flash error, say which was bad
        return "Error reading form values as integers".format()

    print('xx saving', paramRangeSteps)
    # Hour.PARAM_RANGE_STEPS = paramRangeSteps

    # TODO: flash successful
    # TODO: Bug: URL says http://127.0.0.1:5000/doEditParametersSubmit
    # return render_template("parameter-edit.html")
    return redirect(url_for('editParameters'))


@app.route('/doZipSearchSubmit', methods=['POST'])
def doZipSearchSubmit():
    queryVal = request.form.get('query_form_value', None)
    return redirect(url_for('searchForZip', query=queryVal))
