import json
import logging

from flask import render_template, request, redirect, url_for, make_response

from forecast.Forecast import Forecast
from app import app


logger = logging.getLogger(__name__)


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
    URL query parameters:
    o list=true: shows list format for debugging
    o four customized weather parameters (p, t, w, and c) -> use them instead of default.
      there are four, pipe-delimited, one for each parameter: ?p=v1|v2&t=v1|v2|v3|v4&w=v1|v2&c=v1|v2
    :return:
    """
    # todo catch loads error
    rangeDictFromCookie = None
    rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
    if rangesDictJson:
        rangeDictFromCookie = json.loads(rangesDictJson)

    rangeDictFromQuery = None
    try:
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args)
    except ValueError as ve:
        logger.warn("showForecast() ignoring error: {} for args {}".format(ve, request.args))

    zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
    hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
    template = "forecast-list.html" if request.values.get('list') else "forecast.html"

    # handle URL query parameter insertion
    print('xx: query: {}, cookie: {}, args: {}'.format(rangeDictFromQuery, rangeDictFromCookie, request.args))
    try:
        if rangeDictFromQuery:
            # render using customizations in query
            forecast = Forecast(zipOrLatLonList, rangeDictFromQuery)
            return render_template(template, forecast=forecast, hideIcons=hideIcons)
        elif rangeDictFromCookie:
            # redirect back to here using customizations in cookie
            queryParamsDict = queryParamsDictFromRangeDict(rangeDictFromCookie)
            print(' xx redirect: queryParamsDict:', queryParamsDict)
            return redirect(url_for('showForecast', zipOrLatLon=zipOrLatLon, p=queryParamsDict['p'],
                                    t=queryParamsDict['t'], w=queryParamsDict['w'],
                                    c=queryParamsDict['c']))
        else:
            # render using default dict
            forecast = Forecast(zipOrLatLonList)
            return render_template(template, forecast=forecast, hideIcons=hideIcons)
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
    zipOrLatLon = zipOrLatLon.replace(',', '|') # commas are convenient for forms, but pipes are legal chars in URIs, unlike commas which get encoded (%2C)
    return redirect(url_for('showForecast', zipOrLatLon=zipOrLatLon))


@app.route('/edit_display_submit', methods=['POST'])
def do_edit_display_submit():
    isChecked = request.values.get('show_icons_value')
    if isChecked:  # default -> clear cookie
        response = make_response(redirect(url_for('editSettings')))
        response.set_cookie(HIDE_ICONS_COOKIE_NAME, expires=0)
        return response  # todo flash reset and stay on page
    else:  # customized -> set cookie
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


@app.route('/zip_search_submit', methods=['POST'])
def do_zip_search_submit():
    queryVal = request.values.get('query_form_val', None)
    return redirect(url_for('searchForZip', query=queryVal))


# todo refactor to use rangesDictFromRequestArgs()
def rangesDictFromEditFormValues():
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


def rangesDictFromRequestArgs(requestArgs):
    ptwcArgs = [requestArgs.get('p'), requestArgs.get('t'), requestArgs.get('w'), requestArgs.get('c')]
    if not all(ptwcArgs):
        raise ValueError("not all request args were passed: p, t, w, c: {}".format(ptwcArgs))

    pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs = map(lambda x: x.split('|'), ptwcArgs)
    if len(pRangeStrs) != 2 or len(tRangeStrs) != 4 or len(wRangeStrs) != 2 or len(cRangeStrs) != 2:
        raise ValueError("not all string lists had correct # of items: p, t, w, c: {}".
                         format([pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))


    def intsForStrs(intStrs):
        return list(map(int, intStrs))


    try:
        pRangeInts, tRangeInts, wRangeInts, cRangeInts = list(
            map(intsForStrs, [pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))
    except ValueError:
        raise ValueError(
            "not all string lists were integers: {}".format([pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))

    if not all(map(lambda intList: intList == sorted(intList), [pRangeInts, tRangeInts, wRangeInts, cRangeInts])):
        raise ValueError(
            "not all int lists were sorted: p, t, w, c: {}".format([pRangeInts, tRangeInts, wRangeInts, cRangeInts]))

    # finally!
    return {'precip': pRangeInts,
            'temp': tRangeInts,
            'wind': wRangeInts,
            'clouds': cRangeInts}


def queryParamsDictFromRangeDict(rangeDict):
    return {'p': '|'.join(map(str, rangeDict['precip'])),
            't': '|'.join(map(str, rangeDict['temp'])),
            'w': '|'.join(map(str, rangeDict['wind'])),
            'c': '|'.join(map(str, rangeDict['clouds']))
    }
