import datetime
import functools
import logging
import urllib.request
import xml.etree.ElementTree as ET
import operator

from forecast.Hour import Hour

from forecast.Location import Location


logger = logging.getLogger(__name__)


class WeatherGovSource(object):
    """
    Abstract class that represents an online weather source that provides forecast information for a particular
    Location. Stored as a sequence of Hour instances. These have no gaps, i.e., there is one Hour for every hour,
    and all time zone information is normalized. (weather.gov mixes time zones, and has gaps in forecasts.)
    A WeatherSource that uses weather.gov to get forecast data.
    """


    def __repr__(self):
        return '{cls}({location})'.format(
            cls=self.__class__.__name__, location=self.location.__repr__())


    def __init__(self, location, rangeDict, elementTree=None):
        """
        :param location: a Location
        :param rangeDict: optional as in PARAM_RANGE_STEPS_DEFAULT. uses that default if not passed
        :param elementTree: optional ElementTree to use for testing to bypass urlopen() call
        """
        if not isinstance(location, Location):
            raise ValueError("location is not a Location instance: {}".format(location))

        self.location = location
        self.hours = self.makeHours(elementTree, rangeDict)


    def makeHours(self, elementTree, rangeDict):
        """
        :return: a list of Hour instances for location
        """
        if not elementTree:
            httpResponse = urllib.request.urlopen(self.weatherDotGovUrl())
            logger.info('Forecast({}) @ {} -> {}: '.format(
                self.location, datetime.datetime.now(), self.weatherDotGovUrl()))
            elementTree = ET.parse(httpResponse)

        dwmlElement = elementTree.getroot()
        if dwmlElement.tag == 'error':
            errorString = ET.tostring(dwmlElement.find('pre'),
                                      encoding='unicode')  # "xml", "html" or "text" (default xml)
            logger.error(
                "error getting data for zipOrLatLon {}\nurl: \t{}\nerror: {}".format(
                    self.location, self.weatherDotGovUrl(), errorString))
            raise ValueError(errorString)

        return self.hoursWithNoGapsFromXml(dwmlElement, rangeDict)


    def weatherDotGovUrl(self):
        url = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php' \
              '?whichClient=NDFDgen' \
              '&lat={lat}' \
              '&lon={lon}' \
              '&product=time-series' \
              '&Unit=e' \
              '&pop12=pop12' \
              '&appt=appt' \
              '&wspd=wspd' \
              '&sky=sky' \
              '&Submit=Submit'.format(lat=self.location.latitude, lon=self.location.longitude)
        return url


    # ==== hoursWithNoGapsFromXml() and friends ====


    @classmethod
    def hoursWithNoGapsFromXml(cls, dwmlElement, rangeDict):
        """
        Takes the output from hoursWithGapsFromXml() and interpolates missing hoursWithGaps to create a finished list
        of Hours that starts at the first hour in hoursWithGapsFromXml() and finishes with the last.

        :return: a list of Hours starting with the earliest hour in hoursWithGaps and ending with the last,
        where all even hoursWithGaps are represented 
        """
        oneHour = datetime.timedelta(hours=1)
        hoursWithGaps = WeatherGovSource.hoursWithGapsFromXml(dwmlElement, rangeDict)
        oldestHour = hoursWithGaps[0]
        newestHour = hoursWithGaps[-1]

        hoursWithNoGaps = []
        currDatetime = oldestHour.datetime
        prevFoundHour = oldestHour
        while currDatetime <= newestHour.datetime:
            foundHour = WeatherGovSource.findHourForDatetimeFromHoursWithGaps(currDatetime, hoursWithGaps)
            if not foundHour:
                foundHour = Hour(currDatetime, prevFoundHour.precip, prevFoundHour.temp, prevFoundHour.wind,
                                 prevFoundHour.clouds)
            hoursWithNoGaps.append(foundHour)
            prevFoundHour = foundHour
            currDatetime += oneHour
        return hoursWithNoGaps


    def findHourForDatetime(self, theDatetime):
        for hour in self.hours:
            if hour.datetime == theDatetime:
                return hour
        return None


    @classmethod
    def findHourForDatetimeFromHoursWithGaps(cls, theDatetime, hoursWithGaps):
        for hour in hoursWithGaps:
            if hour.datetime == theDatetime:
                return hour
        return None


    @classmethod
    def hoursWithGapsFromXml(cls, dwmlElement, rangeDict):
        """
        :param dwmlElement:
        :return: a sequence of Hour instances corresponding to the passed DWML document element. 
        Note that this list will have gaps between hours because the incoming data itself has gaps, i.e., 
        it's not sampled every hour but (for example) every three or 12 hours. Gaps must be accounted for by callers. 
        Because the forecast data's samples are not the same for all parameters, we need to interpolate missing 
        values by using the most recently seen ones. 
        """
        # 1) build empty Hours with no data based on min and max dates in layoutKeysToStartValidTimes
        timeLayoutDict = cls.timeLayoutDictFromXml(dwmlElement)
        uniqueDatetimes = set(functools.reduce(operator.add, timeLayoutDict.values()))
        hours = list(map(lambda dt: Hour(dt), sorted(uniqueDatetimes)))

        # 2) iterate over weather data and plug into corresponding hour. NB: will leave gaps, i.e., some Hours will not
        # have all three values set
        paramSamplesDict = cls.parameterSamplesDictFromXml(dwmlElement)
        for pName, pVals in paramSamplesDict.items():
            for pVal, pDt in pVals:
                for hour in hours:
                    if hour.datetime == pDt:
                        if pName == 'probability-of-precipitation':
                            hour.precip = pVal
                        elif pName == 'temperature':
                            hour.temp = pVal
                        elif pName == 'wind-speed':
                            hour.wind = pVal
                        elif pName == 'cloud-amount':
                            hour.clouds = pVal
                        else:
                            raise ValueError('invalid parameter name: {} for value {}'.format(pName, pVal))

        # 3) fill in missing data by projecting forward the most recently set value. note that the first item will
        # likely have missing values because there are no older items to project from
        lastPTWC = (None, None, None, None)
        for hour in hours:
            precipTempWind = hour.precip, hour.temp, hour.wind, hour.clouds
            lastPTWC = (precipTempWind[0] if precipTempWind[0] is not None else lastPTWC[0],
                        precipTempWind[1] if precipTempWind[1] is not None else lastPTWC[1],
                        precipTempWind[2] if precipTempWind[2] is not None else lastPTWC[2],
                        precipTempWind[3] if precipTempWind[3] is not None else lastPTWC[3],)
            hour.precip, hour.temp, hour.wind, hour.clouds = lastPTWC

        # 4) remove Hours that still have missing values
        # hours = [hour for hour in hours if all((hour.precip, hour.temp, hour.wind))]
        hours = [hour for hour in hours if hour.precip is not None and hour.temp is not None and hour.wind is not None]
        return hours


    @classmethod
    def timeLayoutDictFromXml(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: dict: {<layout-key> -> [<start-valid-time> datetime instances]}
        """
        timeLayoutDict = {}
        for timeLayoutEle in dwmlElement.findall('data/time-layout'):
            layoutKey = timeLayoutEle.find('layout-key')
            startValidTimes = []
            for startValidTimeEle in timeLayoutEle.findall('start-valid-time'):
                dt = WeatherGovSource.parseStartValidTime(startValidTimeEle.text)
                startValidTimes.append(dt)
            timeLayoutDict[layoutKey.text] = startValidTimes
        return timeLayoutDict


    @classmethod
    def parseStartValidTime(cls, startValidTimeText):
        # e.g., <start-valid-time>2015-01-13T07:00:00-05:00</start-valid-time>. NB: that format is ISO 8601
        # EXCEPT for the ':' in the final time zone section (e.g., '-05:00'), so we remove it before parsing
        startValidTimeText = startValidTimeText[:-3] + startValidTimeText[-2:]
        dt = datetime.datetime.strptime(startValidTimeText, '%Y-%m-%dT%H:%M:%S%z')
        return dt


    @classmethod
    def parameterSamplesDictFromXml(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: dict: {<paramName> -> [(paramVal, paramDatetime)]}
        """
        parameterSamplesDict = {}
        paramDict = cls.parameterDictFromXml(dwmlElement)
        timeLayoutDict = cls.timeLayoutDictFromXml(dwmlElement)
        for paramName, (timeLayoutKey, paramVals) in paramDict.items():
            timeLayoutDatetimes = timeLayoutDict[timeLayoutKey]
            paramSamples = list(zip(paramVals, timeLayoutDatetimes))
            parameterSamplesDict[paramName] = paramSamples
        return parameterSamplesDict


    @classmethod
    def parameterDictFromXml(cls, dwmlElement):
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


