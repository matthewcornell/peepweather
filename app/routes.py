import json
import logging
import urllib.parse

from io import BytesIO
import re
from flask import render_template, request, redirect, url_for, make_response, flash

from forecast.Location import Location
from forecast.ZipCodeUtil import searchZipcodes
from forecast.Forecast import Forecast
from forecast.Sticker import Sticker
from app import app


logger = logging.getLogger(__name__)


# ==== cookie defs ====

HIDE_ICONS_COOKIE_NAME = 'display_preferences'
RANGES_COOKIE_NAME = 'parameter_ranges'

app.secret_key = 'why would I tell you my secret key?'


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
        # make the rangeDict
        rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
        rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get('p') \
            else None  # check for at least one
        rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT

        # make the Forecast
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        forecast = Forecast(Location(zipOrLatLonList), rangeDict)

        # render the forecast
        hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        fullUrl = fullUrlForEndpoint('showForecast', zipOrLatLon, queryParamsDict)
        embedUrl = fullUrlForEndpoint('embedForecast', zipOrLatLon, queryParamsDict)
        template = "forecast-list.html" if request.args.get('list') else "forecast.html"
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
        # make the rangeDict
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or Forecast.PARAM_RANGE_STEPS_DEFAULT

        # make the Forecast
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        forecast = Forecast(Location(zipOrLatLonList), rangeDict)

        # render the forecast
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
        # make the rangeDict
        rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
        rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
        rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
            'p') else None  # check for at least one
        rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT

        # make the Forecast
        zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
        forecast = Forecast(Location(zipOrLatLonList), rangeDict)

        # construct the sticker image
        queryParamsDict = queryParamsDictFromRangeDict(rangeDict)
        stickerImageUrl = fullUrlForEndpoint('generateStickerImage', zipOrLatLon, queryParamsDict)
        image = Sticker(forecast).image
        imageWidth = image.size[0]

        # render the forecast
        forecastUrl = fullUrlForEndpoint('showForecast', zipOrLatLon, queryParamsDict)
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
    # make the rangeDict
    rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
    rangeDictFromCookie = json.loads(rangesDictJson) if rangesDictJson else None
    rangeDictFromQuery = rangesDictFromRequestArgs(request.args) if request.args.get(
        'p') else None  # check for at least one
    rangeDict = rangeDictFromQuery or rangeDictFromCookie or Forecast.PARAM_RANGE_STEPS_DEFAULT

    # make the Forecast
    zipOrLatLonList = zipOrLatLon.split('|') if '|' in zipOrLatLon else zipOrLatLon
    forecast = Forecast(Location(zipOrLatLonList), rangeDict)

    # construct the sticker image and return it as a png
    image = Sticker(forecast).image
    bytesIO = BytesIO()
    image.save(bytesIO, format="png")
    response = make_response(bytesIO.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/search/<query>')
def searchForZip(query):
    zipNameLatLonTuples = searchZipcodes(query)
    if not zipNameLatLonTuples:
        return render_template("message.html", title="No search results for ‘{}’".format(query),
                               message="Please enter a town name or zip code or a comma-separated latitude and "
                                       "longitude.", isError=False)
    else:
        return render_template("search.html", query=query, zipNameLatLonTuples=zipNameLatLonTuples)


@app.route('/settings')
def editSettings():
    rangesDictJson = request.cookies.get(RANGES_COOKIE_NAME)
    if rangesDictJson:
        rangesDict = json.loads(rangesDictJson)
    else:
        rangesDict = Forecast.PARAM_RANGE_STEPS_DEFAULT
    hideIcons = request.cookies.get(HIDE_ICONS_COOKIE_NAME)
    referrer = request.values.get('referrer') or request.referrer
    return render_template("settings.html",
                           referrer=referrer,
                           hideIcons='true' if hideIcons else 'false',
                           precipVals=rangesDict['precip'],
                           tempVals=rangesDict['temp'],
                           windVals=rangesDict['wind'],
                           cloudVals=rangesDict['clouds'])


@app.route('/how-it-works')
def showHowItWorks():
    return render_template("how-it-works.html")


# ==== URL utils ====

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
    zipNameLatLonTuples = searchZipcodes(query)
    locZipResults = set()
    for tup in zipNameLatLonTuples:  # (zipcode, name, latitude, longitude)
        locZipResults.add(tup[1])
    locZipResultsJson = json.dumps(list(locZipResults))
    response = make_response(locZipResultsJson)
    response.mimetype = 'application/json'
    return response


# ==== form handling ====

@app.route('/location_submit', methods=['POST'])
def do_location_submit():
    """
    Called with a single form value to find the forecast for, either a zip code, a lat<comma>lon, or a town/city name
    (partial or typeahead-completed to match zipcode file entry).
    """
    nameOrZipOrLatLon = request.values.get('location_form_val', None)
    if not nameOrZipOrLatLon:
        return render_template("message.html", title="Nothing to search for",
                               message="Please enter a town name or zip code or a comma-separated latitude and longitude.",
                               isError=False)

    # check input format. todo should be done via form flash
    # lat/lon regexp from http://stackoverflow.com/questions/3518504/regular-expression-for-matching-latitude-longitude-coordinates
    nameOrZipOrLatLon = nameOrZipOrLatLon.strip()
    zipMatch = re.search(r'^\d\d\d\d\d$', nameOrZipOrLatLon)
    latLonMatch = re.search(r'^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$', nameOrZipOrLatLon)
    if not zipMatch and not latLonMatch:
        return do_location_search_submit(nameOrZipOrLatLon)

    # use a pipe instead of a comma for lat/long delimiting b/c pipes are legal URI chars, whereas commas get encoded as %2C
    nameOrZipOrLatLon = re.sub(r'\s', '', nameOrZipOrLatLon) \
        .replace(',', '|')
    return redirect(url_for('showForecast', zipOrLatLon=nameOrZipOrLatLon))


def do_location_search_submit(inputName):
    """
    Called when the user searches for a location, perhaps aided by typeahead autocompletion. The search field will
    contain one of three cases:
    1) empty -> show message (no input)
    2) a partial match -> show hits in results page
    3) a unique name thanks to typeahead choice -> show forecast for that one. note that it will be formatted same
       was returned by serveCountries(), i.e., '<city>, <state abbrev>' (ex: 'Bay Minette, AL'), which we need to
       unpack to find the corresponding zip code
    """
    inputName = re.sub(r'/', '', inputName) if inputName else None  # o/w gets treated like a URI
    matchTuples = searchZipcodes(inputName)  # (zipcode, name, latitude, longitude)
    if len(inputName) > 4 and inputName[-4:-2] == ', ':
        # they entered/selected a name that matches one or more, so pick the first one (some names have > 1 zip codes, e.g., 'Chicago, IL')
        zipcode, name, latitude, longitude = matchTuples[0]
        return redirect(url_for('showForecast', zipOrLatLon=zipcode))

    return redirect(url_for('searchForZip', query=inputName))


@app.route('/edit_display_submit', methods=['POST'])
def do_edit_display_submit():
    referrer = request.values.get('referrer')
    isChecked = request.values.get('show_icons_value')
    response = make_response(redirect(url_for('editSettings', referrer=referrer)))
    if isChecked:  # default setting -> clear cookie
        response.set_cookie(HIDE_ICONS_COOKIE_NAME, expires=0)
    else:  # customized setting -> set cookie
        response.set_cookie(HIDE_ICONS_COOKIE_NAME, 'true')
    flash("Show icons is now {}.".format("on" if isChecked else "off"))
    return response


@app.route('/edit_parameters_submit', methods=['POST'])
def do_edit_parameters_submit():
    referrer = request.values.get('referrer')
    isReset = request.values.get('reset_button')
    response = make_response(redirect(url_for('editSettings', referrer=referrer)))
    if isReset:
        response.set_cookie(RANGES_COOKIE_NAME, expires=0)
        flash("Settings have been reset to defaults.")
        return response
    else:
        # save form values as a json dict in the cookie
        try:
            rangesDict = rangesDictFromEditFormValues(request.values)
            rangesDictJson = json.dumps(rangesDict)
            response.set_cookie(RANGES_COOKIE_NAME, rangesDictJson)
            flash("Settings have been saved.")
            return response
        except Exception as ex:
            # todo flash error
            # return render_template("message.html", title="Error setting ranges",
            # message="Some settings were invalid: {}".format(ex), isError=True)
            flash("Some parameters were invalid: {}".format(ex), 'error')
            return redirect(url_for('editSettings', referrer=referrer))


# ==== rangeDict utils ====

def rangesDictFromEditFormValues(requestVals):
    wind_v1_value = requestVals.get('wind_v1_value')
    wind_v2_value = requestVals.get('wind_v2_value')
    precip_v1_value = requestVals.get('precip_v1_value')
    precip_v2_value = requestVals.get('precip_v2_value')
    cloud_v1_value = requestVals.get('cloud_v1_value')
    cloud_v2_value = requestVals.get('cloud_v2_value')
    temp_v1_value = requestVals.get('temp_v1_value')
    temp_v2_value = requestVals.get('temp_v2_value')
    temp_v3_value = requestVals.get('temp_v3_value')
    temp_v4_value = requestVals.get('temp_v4_value')

    pRangeStrs = [precip_v1_value, precip_v2_value]
    tRangeStrs = [temp_v1_value, temp_v2_value, temp_v3_value, temp_v4_value]
    wRangeInts = [wind_v1_value, wind_v2_value]
    cRangeStrs = [cloud_v1_value, cloud_v2_value]

    return rangesDictFromRangeStrs(pRangeStrs, tRangeStrs, wRangeInts, cRangeStrs)


def rangesDictFromRequestArgs(requestArgs):
    ptwcArgs = [requestArgs.get('p'), requestArgs.get('t'), requestArgs.get('w'), requestArgs.get('c')]
    if not all(ptwcArgs):
        raise ValueError("Not all URL query parameters were passed: p, t, w, c: {}".format(ptwcArgs))

    pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs = map(lambda x: x.split('|'), ptwcArgs)
    return rangesDictFromRangeStrs(pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs)


def rangesDictFromRangeStrs(pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs):
    """
    :return: a range dict akin to Forecast.PARAM_RANGE_STEPS_DEFAULT corresponding to the args, which are either 2-tuple
    (pRangeStrs, wRangeStrs, cRangeStrs) or 4-tuple (tRangeStrs) lists of (ideally int) strings
    """
    if len(pRangeStrs) != 2 or len(tRangeStrs) != 4 or len(wRangeStrs) != 2 or len(cRangeStrs) != 2:
        raise ValueError("Not all parameters had correct # of items: precip: {}, temp: {}, wind: {}, clouds: {}".format(
            pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs))


    def intsForStrs(intStrs):
        return list(map(int, intStrs))


    try:
        pRangeInts, tRangeInts, wRangeInts, cRangeInts = list(
            map(intsForStrs, [pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs]))
    except ValueError:
        raise ValueError(
            "Not all  parameters were integers: precip: {}, temp: {}, wind: {}, clouds: {}".format(
                pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs))

    if not all(map(lambda intList: intList == sorted(intList), [pRangeInts, tRangeInts, wRangeInts, cRangeInts])):
        raise ValueError(
            "Not all parameters were sorted: precip: {}, temp: {}, wind: {}, clouds: {}".format(
                pRangeStrs, tRangeStrs, wRangeStrs, cRangeStrs))

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
