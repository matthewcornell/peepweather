from io import StringIO, BytesIO
import json
import logging
import urllib.parse

from flask import render_template, request, redirect, url_for, make_response
from PIL import Image

from forecast.Forecast import Forecast
from app import app


logger = logging.getLogger(__name__)


# ==== routes ====

HIDE_ICONS_COOKIE_NAME = 'display_preferences'
RANGES_COOKIE_NAME = 'parameter_ranges'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/embed/<zipOrLatLon>')
def embedForecast(zipOrLatLon):
    """
    same inputs and query parameters as showForecast() but returns a simpler HTML document suitable for an <iframe> embedding
    """
    try:
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or Forecast.PARAM_RANGE_STEPS_DEFAULT
        forecast = Forecast(zipOrLatLonList, rangeDictFromQuery)
        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        urlToShare = url_for('showForecast', zipOrLatLon=zipOrLatLon,
                             _external=True,
                             p=queryParamsDict['p'], t=queryParamsDict['t'], w=queryParamsDict['w'],
                             c=queryParamsDict['c'])
        fullUrl = urllib.parse.unquote(urlToShare)
        return render_template("embedded-forecast.html", forecast=forecast, fullUrl=fullUrl)
    except Exception as ex:
        return render_template("embedded-forecast.html", error=ex.args[0])


@app.route('/forecaststicker/<zipOrLatLon>')
def generateStickerImage(zipOrLatLon):
    """
    :param zipOrLatLon:
    todo pass customization query args like showForecast(), but not list
    """
    zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
    forecast = Forecast(zipOrLatLonList)
    image = imageForForecast(forecast)
    bytesIO = BytesIO()
    image.save(bytesIO, format="png")
    response = make_response(bytesIO.getvalue())
    response.mimetype = 'image/png'
    return response 


@app.route('/stickers/<zipOrLatLon>')
def showStickersEditor(zipOrLatLon):
    """
    :param zipOrLatLon: same as showForecast()
    URL query parameters: none
    """
    try:
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        forecast = Forecast(zipOrLatLonList)
        stickerCode = render_template("sticker-code.html", forecast=forecast, zipOrLatLon=zipOrLatLon)
        return render_template("stickers.html", forecast=forecast, stickerCode=stickerCode, zipOrLatLon=zipOrLatLon)
    except Exception as ex:
        return render_template("message.html", title="Error getting forecast", message=ex.args[0], isError=True)


def imageForForecast(forecast):
    # get a temporary png file so we have an Image to work with. later it will be generated
    # dynamically - Sticker.generateImage(forecast)
    import os
    cwd = os.getcwd()
    imagePath = url_for('static', filename='sticker-126x187-temp.png')  # /static/sticker-126x187-temp.png
    fullPath = cwd + os.sep + 'app' + os.sep + imagePath
    image = Image.open(fullPath)
    return image


@app.route('/forecast/<zipOrLatLon>')
def showForecast(zipOrLatLon):
    """
    :param zipOrLatLon: location to get the forecast for. either a zip code string or a comma-separated list of
    latitude and longitude strings. ex: '01002' or '42.375370,-72.519249'.
    URL query parameters:
    o list=true: shows list format for debugging
    o four customized weather parameters (p, t, w, and c) -> use them instead of default.
      there are four, pipe-delimited, one for each parameter: ?p=v1|v2&t=v1|v2|v3|v4&w=v1|v2&c=v1|v2
    """
    try:
        rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
        rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT
        template = "forecast-list.html" if request.args.get('list') else "forecast.html"
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        forecast = Forecast(zipOrLatLonList, rangeDict)
        hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        fullUrl = urllib.parse.unquote(
            url_for('showForecast', zipOrLatLon=zipOrLatLon, _external=True, p=queryParamsDict['p'],
                    t=queryParamsDict['t'], w=queryParamsDict['w'], c=queryParamsDict['c']))
        embedUrl = urllib.parse.unquote(
            url_for('embedForecast', zipOrLatLon=zipOrLatLon, _external=True, p=queryParamsDict['p'],
                    t=queryParamsDict['t'], w=queryParamsDict['w'], c=queryParamsDict['c']))
        return render_template(template, forecast=forecast, hideIcons=hideIcons, fullUrl=fullUrl, embedUrl=embedUrl)
    except Exception as ex:
        return render_template("message.html", title="Error getting forecast", message=ex.args[0], isError=True)


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
    zipNameLatLonTuples = Forecast.searchZipcodes(query)
    if not zipNameLatLonTuples:
        return render_template("message.html", title="No search results for ‘{}’".format(query),
                               message="The search feature is primitive, so try a single word or part of one, " +
                                       "such as 'york', instead of new york, new york. Also, spaces " +
                                       "and commas cause trouble, as do state names/abbreviations", isError=False)
    else:
        return render_template("search.html", query=query, zipNameLatLonTuples=zipNameLatLonTuples)


@app.route('/how-it-works')
def showHowItWorks():
    return render_template("how-it-works.html")


# ==== forms ====

@app.route('/submit_zip', methods=['POST'])
def do_zip_submit():
    zipOrLatLon = request.values.get('zip_or_latlon_form_val', None)
    if not zipOrLatLon:
        return render_template("message.html", title="Nothing to search for",
                               message="Please enter a zip code or a latitude, longitude.", isError=False)
    else:
        zipOrLatLon = zipOrLatLon.replace(',',
                                          '|')  # commas are convenient for forms, but pipes are legal chars in URIs, unlike commas which get encoded (%2C)
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
    if not queryVal:
        return render_template("message.html", title="Nothing to search for",
                               message="Please enter a search term.", isError=False)
    else:
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
        raise ValueError("Not all query parameters were passed: p, t, w, c: {}".format(ptwcArgs))

    pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs = map(lambda x: x.split('|'), ptwcArgs)
    if len(pRangeStrs) != 2 or len(tRangeStrs) != 4 or len(wRangeStrs) != 2 or len(cRangeStrs) != 2:
        raise ValueError("Not all query parameters had correct # of items: p, t, w, c: {}".
                         format([pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))


    def intsForStrs(intStrs):
        return list(map(int, intStrs))


    try:
        pRangeInts, tRangeInts, wRangeInts, cRangeInts = list(
            map(intsForStrs, [pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))
    except ValueError:
        raise ValueError(
            "Not all query parameters were integers: {}".format([pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))

    if not all(map(lambda intList: intList == sorted(intList), [pRangeInts, tRangeInts, wRangeInts, cRangeInts])):
        raise ValueError(
            "Not all query parameters were sorted: p, t, w, c: {}".format(
                [pRangeInts, tRangeInts, wRangeInts, cRangeInts]))

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
