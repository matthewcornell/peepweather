import json
import logging
import urllib.parse

from io import BytesIO
from flask import render_template, request, redirect, url_for, make_response
import re

from forecast.Forecast import Forecast
from forecast.Sticker import Sticker
from app import app


logger = logging.getLogger(__name__)


# ==== cookies ====

HIDE_ICONS_COOKIE_NAME = 'display_preferences'
RANGES_COOKIE_NAME = 'parameter_ranges'


# ==== routes ====

@app.route('/')
def index():
    return render_template("index.html")


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
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
        rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT
        template = "forecast-list.html" if request.args.get('list') else "forecast.html"
        forecast = Forecast(zipOrLatLonList, rangeDict)
        hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        fullUrl = fullUrlForEndpoint('showForecast', zipOrLatLon, queryParamsDict)
        embedUrl = fullUrlForEndpoint('embedForecast', zipOrLatLon, queryParamsDict)
        return render_template(template, forecast=forecast, hideIcons=hideIcons,
                               fullUrl=fullUrl, embedUrl=embedUrl,
                               zipOrLatLon=zipOrLatLon)
    except Exception as ex:
        return render_template("message.html", title="Error getting forecast", message=ex.args[0], isError=True)


@app.route('/embed/<zipOrLatLon>')
def embedForecast(zipOrLatLon):
    """
    :param zipOrLatLon:
    URL query parameters: same as showForecast(), but not list
    """
    try:
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or Forecast.PARAM_RANGE_STEPS_DEFAULT
        forecast = Forecast(zipOrLatLonList, rangeDict)

        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        fullUrl = fullUrlForEndpoint('showForecast', zipOrLatLon, queryParamsDict)
        return render_template("embedded-forecast.html", forecast=forecast, fullUrl=fullUrl)
    except Exception as ex:
        return render_template("embedded-forecast.html", error=ex.args[0])


@app.route('/stickers/<zipOrLatLon>')
def showStickersEditor(zipOrLatLon):
    """
    :param zipOrLatLon: same as showForecast()
    URL query parameters: same as showForecast(), but not list
    """
    try:
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
        rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT
        forecast = Forecast(zipOrLatLonList, rangeDict)
        image = Sticker(forecast).image

        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        forecastUrl = fullUrlForEndpoint('showForecast', zipOrLatLon, queryParamsDict)
        stickerImageUrl = fullUrlForEndpoint('generateStickerImage', zipOrLatLon, queryParamsDict)
        imageWidth = image.size[0]
        stickerCode = render_template("sticker-code.html", forecast=forecast,
                                      forecastUrl=forecastUrl, stickerImageUrl=stickerImageUrl,
                                      imageWidth=imageWidth)
        return render_template("stickers.html", forecast=forecast,
                               forecastUrl=forecastUrl, stickerImageUrl=stickerImageUrl,
                               imageWidth=imageWidth, stickerCode=stickerCode)
    except Exception as ex:
        return render_template("message.html", title="Error getting forecast", message=ex.args[0], isError=True)


@app.route('/forecaststicker/<zipOrLatLon>')
def generateStickerImage(zipOrLatLon):
    """
    :param zipOrLatLon:
    URL query parameters: same as showForecast(), but not list
    """
    zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
    rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
    rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
    rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
        'p') else None  # check for at least one
    rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT
    forecast = Forecast(zipOrLatLonList, rangeDict)
    image = Sticker(forecast).image
    bytesIO = BytesIO()
    image.save(bytesIO, format="png")
    response = make_response(bytesIO.getvalue())
    response.mimetype = 'image/png'
    return response


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


def fullUrlForEndpoint(endpoint, zipOrLatLon, queryParamsDict):
    url = urllib.parse.unquote(
        url_for(endpoint, zipOrLatLon=zipOrLatLon, _external=True, p=queryParamsDict['p'],
                t=queryParamsDict['t'], w=queryParamsDict['w'], c=queryParamsDict['c']))
    return url


# ==== APIs ====

@app.route('/place/<query>')
def searchLocationsJson(query):
    """
    Called by the typeahead library, searches for locations containing <query> and returns a JSON list of matching
    names in the format returned by searchZipcodes(), i.e., "<city>, <state abbrev>"
    """
    zipNameLatLonTuples = Forecast.searchZipcodes(query)
    locZipResults = set()
    for tup in zipNameLatLonTuples:  # (zipcode, name, latitude, longitude)
        locZipResults.add(tup[1])
    locZipResultsJson = json.dumps(list(locZipResults))
    response = make_response(locZipResultsJson)
    response.mimetype = 'application/json'
    return response


# ==== forms ====

@app.route('/zip_submit', methods=['POST'])
def do_zip_or_latlon_submit():
    zipOrLatLon = request.values.get('zip_or_latlon_form_val', None)
    if not zipOrLatLon:
        return render_template("message.html", title="Nothing to search for",
                               message="Please enter a zip code or a comma-separated latitude and longitude.",
                               isError=False)

    # check input format. todo should be done via form flash, e.g., WTF + Flask flash. for now show message
    # lat/lon regexp from http://stackoverflow.com/questions/3518504/regular-expression-for-matching-latitude-longitude-coordinates
    zipOrLatLon = re.sub(r'\s', '', zipOrLatLon)
    zipMatch = re.search(r'^\d\d\d\d\d$', zipOrLatLon)
    latLonMatch = re.search(r'^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$', zipOrLatLon)
    if not zipMatch and not latLonMatch:
        return render_template("message.html", title="Invalid zip code or latitude/longitude format",
                               message="Input must be either a five-digit zip code or a comma-separated latitude "
                                       "and longitude.", isError=False)
    
    # use a pipe instead of a comma for lat/long delimiting b/c pipes are legal URI chars, whereas commas get encoded as %2C
    zipOrLatLon = zipOrLatLon.replace(',', '|')
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


@app.route('/location_search_submit', methods=['POST'])
def do_location_search_submit():
    """
    Called when the user searches for a location, perhaps aided by typeahead autocompletion. The search field will
    contain one of three cases:
    1) empty -> show message (no input)
    2) a partial match -> show hits in results page
    3) a unique name thanks to typeahead choice -> show forecast for that one. note that it will be formatted same
       was returned by serveCountries(), i.e., '<city>, <state abbrev>' (ex: 'Bay Minette, AL'), which we need to
       unpack to find the corresponding zip code
    """
    inputName = request.values.get('search_field')
    inputName = re.sub(r'/', '', inputName) if inputName else None  # o/w gets treated like a URI
    if not inputName:
        return render_template("message.html", title="Nothing to search for",
                               message="Please enter a town or city name.", isError=False)

    matchTuples = Forecast.searchZipcodes(inputName)  # (zipcode, name, latitude, longitude)
    if len(inputName) > 4 and inputName[-4:-2] == ', ':
        # they entered/selected a name that matches one or more, so pick the first one (some names have > 1 zip codes, e.g., 'Chicago, IL')
        zipcode, name, latitude, longitude = matchTuples[0]
        return redirect(url_for('showForecast', zipOrLatLon=zipcode))

    return redirect(url_for('searchForZip', query=inputName))


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
