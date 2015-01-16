from datetime import datetime
import functools
import operator
import urllib.request
import xml.etree.ElementTree as ET
import re
import logging

from forecast.Hour import Hour
from forecast import CACHED_ZIP_INFO_TUPLES


logger = logging.getLogger(__name__)


class Forecast:
    def __init__(self, zipcode, elementTree=None):
        """
        :param zipcode: str zip code to get forecast for
        :param elementTree: optional ElementTree to use for testing to bypass urlopen() call
        :return:
        """
        (lat, lon, name) = self.latLonNameForZipcode(zipcode)
        self.zipcode = zipcode
        self.latLon = (lat, lon)
        self.name = name
        self.error = False

        if not elementTree:
            httpResponse = urllib.request.urlopen(self.weatherDotGovUrl())
            elementTree = ET.parse(httpResponse)
        dwmlElement = elementTree.getroot()
        logMsg = 'Forecast({}): {}, {}, {} {}, {}'.format(
            zipcode, (lat, lon), name, self.weatherDotGovUrl(), elementTree, dwmlElement)
        logger.info("logger.info: " + logMsg)
        print("(print): " + logMsg)
        
        if dwmlElement.tag == 'error':
            self.error = True
            self.error = ET.tostring(dwmlElement.find('pre'), encoding='unicode')   # "xml", "html" or "text" (default xml)
            logger.error("error getting data for zipcode {}: {}".format(zipcode, self.error))
        else:
            self.hours = self.hoursFromDwmlXmlRoot(dwmlElement)


    def __repr__(self):
        return '{cls}({zipcode})'.format(cls=self.__class__.__name__, zipcode=self.zipcode)


    def weatherDotGovUrl(self):
        url = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php' \
              '?whichClient=NDFDgen' \
              '&lat={lat}' \
              '&lon={lon}' \
              '&product=time-series' \
              '&Unit=e' \
              '&temp=temp' \
              '&pop12=pop12' \
              '&wspd=wspd' \
              '&Submit=Submit'.format(lat=self.latLon[0], lon=self.latLon[1])
        return url


    #
    # Hours search
    #

    def getHour(self, dayOfWeek, hourOfDay):
        """
        :param dayOfWeek: same as datetime.weekday() - Monday is 0 and Sunday is 6
        :param hourOfDay: same as datetime.hour - range(24)
        :return: the first Hour in my hours that matches the inputs
        """
        for hour in self.hours:
            if hour.getDayOfWeek() == dayOfWeek and hour.getHourOfDay() == hourOfDay:
                return hour
        return Hour()   # missing hour


    #
    # zipcode utilities
    #

    @staticmethod
    def latLonNameForZipcode(zipcode):
        """
        :param zipcode:
        :return: looks up and returns information for zipcode as a 3-tuple of the form: (latitude, longitude, name)
        """
        for (csv_zipcode, city, state, latitude, longitude) in CACHED_ZIP_INFO_TUPLES:
            if csv_zipcode == zipcode:
                return latitude, longitude, city + ", " + state
        raise ValueError("invalid zipcode: {}".format(zipcode))


    @classmethod
    def searchZipcodes(cls, query):
        """
        :param query: 
        :return: a list of 2-tuples containing places matching query. format: (zipcode, name), where name is the same
        as latLonNameForZipcode()
        """
        zipNameTuples = []
        for (csv_zipcode, city, state, latitude, longitude) in CACHED_ZIP_INFO_TUPLES:
            name = city + ", " + state
            if re.search(query, name, re.IGNORECASE):
                zipNameTuples.append((csv_zipcode, name))
        return zipNameTuples


    #
    # hoursFromDwmlXmlRoot() and friends
    #


    @classmethod
    def hoursFromDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: a sequence of Hour instances corresponding to the passed DWML document element. Note that this list
        will have gaps between hours because the incoming data itself has gaps, i.e., it's not sampled every hour but
        (for example) every three or 12 hours. Gaps must be accounted for by callers.
        """
        # 1) build empty Hours with no data based on min and max dates in layoutKeysToStartValidTimes
        timeLayoutDict = cls.timeLayoutDictFromDwmlXmlRoot(dwmlElement)
        uniqueDatetimes = set(functools.reduce(operator.add, timeLayoutDict.values()))
        hours = list(map(lambda dt: Hour(dt), sorted(uniqueDatetimes)))

        # 2) iterate over weather data and plug into corresponding hour. NB: will leave gaps, i.e., some Hours will not
        # have all three values set
        paramSamplesDict = cls.parameterSamplesDictFromDwmlXmlRoot(dwmlElement)
        for pName, pVals in paramSamplesDict.items():
            for pVal, pDt in pVals:
                for hour in hours:
                    if hour.datetime == pDt:
                        if pName == 'probability-of-precipitation':
                            hour.precip = pVal
                        elif pName == 'temperature':
                            hour.temp = pVal
                        else:  # 'wind-speed'
                            hour.wind = pVal

        # 3) fill in missing data by projecting forward the most recently set value. note that the first item will
        # likely have missing values because there are no older items to project from
        lastPrecipTempWind = (None, None, None)
        for hour in hours:
            precipTempWind = hour.precip, hour.temp, hour.wind
            lastPrecipTempWind = (precipTempWind[0] if precipTempWind[0] is not None else lastPrecipTempWind[0],
                                  precipTempWind[1] if precipTempWind[1] is not None else lastPrecipTempWind[1],
                                  precipTempWind[2] if precipTempWind[2] is not None else lastPrecipTempWind[2])
            hour.precip, hour.temp, hour.wind = lastPrecipTempWind

        # 4) remove Hours that still have missing values
        # hours = [hour for hour in hours if all((hour.precip, hour.temp, hour.wind))]
        hours = [hour for hour in hours if hour.precip is not None and hour.temp is not None and hour.wind is not None]
        return hours


    @classmethod
    def timeLayoutDictFromDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: dict: {<layout-key> -> [<start-valid-time> datetime instances]}
        """
        timeLayoutDict = {}
        for timeLayoutEle in dwmlElement.findall('data/time-layout'):
            layoutKey = timeLayoutEle.find('layout-key')
            startValidTimes = []
            for startValidTimeEle in timeLayoutEle.findall('start-valid-time'):
                # e.g., <start-valid-time>2015-01-13T07:00:00-05:00</start-valid-time>. NB: that format is ISO 8601
                # EXCEPT for the ':' in the final time zone section (e.g., '-05:00'), so we remove it before parsing
                startValidTimeTrim = startValidTimeEle.text[:-3] + startValidTimeEle.text[-2:]
                dt = datetime.strptime(startValidTimeTrim, '%Y-%m-%dT%H:%M:%S%z')
                startValidTimes.append(dt)
            timeLayoutDict[layoutKey.text] = startValidTimes
        return timeLayoutDict


    @classmethod
    def parameterSamplesDictFromDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: dict: {<paramName> -> [(paramVal, paramDatetime)]}
        """
        parameterSamplesDict = {}
        paramDict = cls.parameterDictFromDwmlXmlRoot(dwmlElement)
        timeLayoutDict = cls.timeLayoutDictFromDwmlXmlRoot(dwmlElement)
        for paramName, (timeLayoutKey, paramVals) in paramDict.items():
            timeLayoutDatetimes = timeLayoutDict[timeLayoutKey]
            paramSamples = list(zip(paramVals, timeLayoutDatetimes))
            parameterSamplesDict[paramName] = paramSamples
        return parameterSamplesDict


    @classmethod
    def parameterDictFromDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: dict: {<name> -> (<time-layout>, [int values])}
        """
        paramDict = {}
        for paramEle in dwmlElement.find('data/parameters'):
            paramVals = list(map(lambda val: int(val.text), paramEle.findall('value')))
            timeLayout = paramEle.attrib['time-layout']
            paramDict[paramEle.tag] = (timeLayout, paramVals)
        return paramDict
