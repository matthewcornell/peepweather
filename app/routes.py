import json

from flask import render_template, request, redirect, url_for, make_response

from forecast.Forecast import Forecast
from app import app


# ==== routes ====

RANGES_COOKIE_NAME = 'parameter_ranges'
TEXT_ICON_COOKIE_NAME = 'text_icons_enabled'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/forecast/<zipOrLatLon>')
def showForecast(zipOrLatLon):
    """
    :param zipOrLatLon: location to get the forecast for. either a zip code string or a comma-separated list of
    latitude and longitude strings. ex: '01002' or '42.375370,-72.519249'
    Query parameters: Three comma-separated lists of integers, as returned by Forecast.urlQueryParamsForDefaultRanges().
    All three are always required for a forecast: precip_steps, temp_steps, wind_steps.
    
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
            return render_template("forecast.html", forecast=forecast,
                                   useTextIcons=request.cookies.get(TEXT_ICON_COOKIE_NAME))
    except ValueError as ve:
        return render_template("forecast-error.html", error=ve.args[0])


@app.route('/ranges')
def editRanges():
    rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
    if rangesDictJson:
        rangesDict = json.loads(rangesDictJson)
    else:
        rangesDict = Forecast.PARAM_RANGE_STEPS_DEFAULT
    return render_template("edit-ranges.html",
                           precipVals=rangesDict['precip'],
                           tempVals=rangesDict['temp'],
                           windVals=rangesDict['wind'])


@app.route('/search/<query>')
def searchForZip(query):
    return render_template("search.html", query=query, zipNameLatLonTuples=Forecast.searchZipcodes(query))


# ==== forms ====

@app.route('/submit_zip', methods=['POST'])
def do_zip_submit():
    zipVal = request.values.get('zip_form_value', None)
    return redirect(url_for('showForecast', zipOrLatLon=zipVal))


@app.route('/lat_lon_submit', methods=['POST'])
def do_lat_lon_submit():
    latVal = request.values.get('lat_form_value', None)
    lonVal = request.values.get('lon_form_value', None)
    return redirect(url_for('showForecast', zipOrLatLon=latVal + ',' + lonVal))


@app.route('/edit_parameters_submit', methods=['POST'])
def do_edit_parameters_submit():
    isReset = request.values.get('reset_button')
    if isReset:
        # reset (expire) the cookie
        response = make_response(redirect(url_for('editRanges')))
        response.set_cookie(RANGES_COOKIE_NAME, expires=0)
        return response  # todo flash reset and stay on page
    else:
        # save form values as a json dict in the cookie
        try:
            rangesDict = rangesDictFromEditFormValues()
            # todo validate rangeDict - all ints increasing, for example
            rangesDictJson = json.dumps(rangesDict)
            response = make_response(redirect(url_for('editRanges')))
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
    temp_v1_value = request.values.get('temp_v1_value')
    temp_v2_value = request.values.get('temp_v2_value')
    temp_v3_value = request.values.get('temp_v3_value')
    temp_v4_value = request.values.get('temp_v4_value')
    rangesDict = {'precip': list(map(int, [precip_v1_value, precip_v2_value])),
                  'temp': list(map(int, [temp_v1_value, temp_v2_value, temp_v3_value, temp_v4_value])),
                  'wind': list(map(int, [wind_v1_value, wind_v2_value]))}
    return rangesDict


@app.route('/zip_search_submit', methods=['POST'])
def do_zip_search_submit():
    queryVal = request.values.get('query_form_value', None)
    return redirect(url_for('searchForZip', query=queryVal))


@app.route('/text_icon_submit', methods=['POST'])
def do_text_icon_submit():
    if request.values.get('enable_button', None):
        response = make_response(redirect(url_for('index')))
        response.set_cookie(TEXT_ICON_COOKIE_NAME, 'True')
        return response  # todo flash saved and stay on page
    else:
        # reset (expire) the cookie
        response = make_response(redirect(url_for('index')))
        response.set_cookie(TEXT_ICON_COOKIE_NAME, expires=0)
        return response  # todo flash reset and stay on page
