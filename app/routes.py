import json

from flask import render_template, request, redirect, url_for, make_response

from forecast.Forecast import Forecast
from app import app


# ==== routes ====

HIDE_ICONS_COOKIE_NAME = 'display_preferences'
RANGES_COOKIE_NAME = 'parameter_ranges'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/forecast/')
def showForecastNoZip():
    return redirect(url_for('index'))
    

@app.route('/forecast/<zipOrLatLon>')
def showForecast(zipOrLatLon):
    """
    :param zipOrLatLon: location to get the forecast for. either a zip code string or a comma-separated list of
    latitude and longitude strings. ex: '01002' or '42.375370,-72.519249'.
    URL query parameters: Accepts one: ?list=true , which shows a debugging output
    :return:
    """
    try:
        if ',' in zipOrLatLon:
            zipOrLatLonList = zipOrLatLon.split(',')
        else:
            zipOrLatLonList = zipOrLatLon

        rangeDict = None
        rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
        if rangesDictJson:
            rangeDict = json.loads(rangesDictJson)

        forecast = Forecast(zipOrLatLonList, rangeDict)
        if request.values.get('list'):
            return render_template("forecast-list.html", forecast=forecast)
        else:
            hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
            return render_template("forecast.html", forecast=forecast, hideIcons=hideIcons)
    except ValueError as ve:
        return render_template("forecast-error.html", error=ve.args[0])


@app.route('/settings')
def editSettings():
    rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
    hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
    if rangesDictJson:
        rangesDict = json.loads(rangesDictJson)
    else:
        rangesDict = Forecast.PARAM_RANGE_STEPS_DEFAULT
    return render_template("settings.html",
                           hideIcons='true' if hideIcons else 'false',
                           precipVals=rangesDict['precip'],
                           tempVals=rangesDict['temp'],
                           windVals=rangesDict['wind'],
                           cloudVals=rangesDict['clouds'])


@app.route('/search/<query>')
def searchForZip(query):
    return render_template("search.html", query=query, zipNameLatLonTuples=Forecast.searchZipcodes(query))


@app.route('/how-it-works')
def showHowItWorks():
    return render_template("how-it-works.html")


# ==== forms ====

@app.route('/submit_zip', methods=['POST'])
def do_zip_submit():
    zipOrLatLon = request.values.get('zip_or_latlon_form_val', None)
    return redirect(url_for('showForecast', zipOrLatLon=zipOrLatLon))


@app.route('/edit_display_submit', methods=['POST'])
def do_edit_display_submit():
    isChecked = request.values.get('show_icons_value')
    if isChecked:   # default -> clear cookie
        response = make_response(redirect(url_for('editSettings')))
        response.set_cookie(HIDE_ICONS_COOKIE_NAME, expires=0)
        return response  # todo flash reset and stay on page
    else:           # customized -> set cookie
        response = make_response(redirect(url_for('editSettings')))
        response.set_cookie(HIDE_ICONS_COOKIE_NAME, 'true')
        return response  # todo flash saved and stay on page


@app.route('/edit_parameters_submit', methods=['POST'])
def do_edit_parameters_submit():
    isReset = request.values.get('reset_button')
    if isReset:
        response = make_response(redirect(url_for('editSettings')))
        response.set_cookie(RANGES_COOKIE_NAME, expires=0)
        return response  # todo flash reset and stay on page
    else:
        # save form values as a json dict in the cookie
        try:
            rangesDict = rangesDictFromEditFormValues()
            # todo validate rangeDict - all ints increasing, for example
            rangesDictJson = json.dumps(rangesDict)
            response = make_response(redirect(url_for('editSettings')))
            response.set_cookie(RANGES_COOKIE_NAME, rangesDictJson)
            return response  # todo flash saved and stay on page
        except Exception as ex:
            # todo flash error
            return 'error setting ranges - some were invalid: {}'.format(ex)


def rangesDictFromEditFormValues():
    # todo error check -> cleaner exception messages
    wind_v1_value = request.values.get('wind_v1_value')
    wind_v2_value = request.values.get('wind_v2_value')
    precip_v1_value = request.values.get('precip_v1_value')
    precip_v2_value = request.values.get('precip_v2_value')
    cloud_v1_value = request.values.get('cloud_v1_value')
    cloud_v2_value = request.values.get('cloud_v2_value')
    temp_v1_value = request.values.get('temp_v1_value')
    temp_v2_value = request.values.get('temp_v2_value')
    temp_v3_value = request.values.get('temp_v3_value')
    temp_v4_value = request.values.get('temp_v4_value')
    rangesDict = {'precip': list(map(int, [precip_v1_value, precip_v2_value])),
                  'temp': list(map(int, [temp_v1_value, temp_v2_value, temp_v3_value, temp_v4_value])),
                  'wind': list(map(int, [wind_v1_value, wind_v2_value])),
                  'clouds': list(map(int, [cloud_v1_value, cloud_v2_value])),
                  }
    return rangesDict


@app.route('/zip_search_submit', methods=['POST'])
def do_zip_search_submit():
    queryVal = request.values.get('query_form_val', None)
    return redirect(url_for('searchForZip', query=queryVal))
