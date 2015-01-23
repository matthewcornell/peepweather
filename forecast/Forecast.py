import datetime
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
    """
    Computes a forecast based on a zip code using http://www.nws.noaa.gov/ndfd/technical.htm as a sequence of Hours.
    """
    def __init__(self, zipOrLatLon, elementTree=None):
        """
        :param zipOrLatLon: location to get the forecast for. either a zip code string or a 2-tuple of latitude and
        longitude strings. ex: '01002' or ('42.375370', '-72.519249').
        :param elementTree: optional ElementTree to use for testing to bypass urlopen() call
        :return:
        """
        if type(zipOrLatLon) == str:
            self.zipcode = zipOrLatLon
            (lat, lon, name) = self.latLonNameForZipcode(zipOrLatLon)
            self.latLon = (lat, lon)
            self.name = name
        elif type(zipOrLatLon) == list and len(zipOrLatLon) == 2 \
                and type(zipOrLatLon[0]) == str \
                and type(zipOrLatLon[1]) == str:
            self.zipcode = None
            self.latLon = zipOrLatLon
            self.name = None
        else:
            raise ValueError("invalid zipOrLatLon {}".format(zipOrLatLon))
        
        if not elementTree:
            httpResponse = urllib.request.urlopen(self.weatherDotGovUrl())
            print('Forecast({}) @ {}: {}, {} -> {}: '.format(
                self.zipcode, datetime.datetime.now(), self.latLon, self.name, self.weatherDotGovUrl()))
            elementTree = ET.parse(httpResponse)
        dwmlElement = elementTree.getroot()
        if dwmlElement.tag == 'error':
            errorString = ET.tostring(dwmlElement.find('pre'), encoding='unicode')  # "xml", "html" or "text" (default xml)
            logger.error(
                "error getting data for zipOrLatLon {}\nurl: \t{}\nerror: {}".format(
                    zipOrLatLon, self.weatherDotGovUrl(), errorString))
            raise ValueError(errorString)

        # no error
        self.hours = Forecast.hoursWithNoGapsFromXml(dwmlElement)


    def __repr__(self):
        return '{cls}({zipcode})'.format(cls=self.__class__.__name__, zipcode=self.zipcode)
    
    
    def location(self):
        if self.name and self.zipcode:
            return '{} ({})'.format(self.zipcode, self.name)
        else:
            return '{}, {}'.format(self.latLon[0], self.latLon[1])


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
        raise ValueError("couldn't find zipcode: {}".format(zipcode))


    @classmethod
    def searchZipcodes(cls, query):
        """
        :param query: 
        :return: a list of 4-tuples containing places matching query. format: (zipcode, name, latitude, longitude),
        where name is the same as latLonNameForZipcode()
        """
        zipNameTuples = []
        for (csv_zipcode, city, state, latitude, longitude) in CACHED_ZIP_INFO_TUPLES:
            name = city + ", " + state
            if re.search(query, name, re.IGNORECASE):
                zipNameTuples.append((csv_zipcode, name, latitude, longitude))
        return zipNameTuples


    #
    # hoursWithNoGapsFromXml() and friends
    #


    @classmethod
    def hoursWithNoGapsFromXml(cls, dwmlElement):
        """
        Takes the output from hoursWithGapsFromXml() and interpolates missing hoursWithGaps to create a finished list
        of Hours that starts at the first hour in hoursWithGapsFromXml() and finishes with the last.

        :return: a list of Hours starting with the earliest hour in hoursWithGaps and ending with the last,
        where all even hoursWithGaps are represented 
        """
        oneHour = datetime.timedelta(hours=1)
        hoursWithGaps = Forecast.hoursWithGapsFromXml(dwmlElement)
        oldestHour = hoursWithGaps[0]
        newestHour = hoursWithGaps[-1]

        hoursWithNoGaps = []
        currDatetime = oldestHour.datetime
        prevFoundHour = oldestHour
        while currDatetime <= newestHour.datetime:
            foundHour = Forecast.findHourForDatetime(currDatetime, hoursWithGaps)
            if not foundHour:
                foundHour = Hour(currDatetime, prevFoundHour.precip, prevFoundHour.temp, prevFoundHour.wind)
            hoursWithNoGaps.append(foundHour)
            prevFoundHour = foundHour
            currDatetime += oneHour
        return hoursWithNoGaps


    @classmethod
    def findHourForDatetime(cls, theDatetime, hoursWithGaps):
        for hour in hoursWithGaps:
            if hour.datetime == theDatetime:
                return hour
        return None


    @classmethod
    def hoursWithGapsFromXml(cls, dwmlElement):
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
                # e.g., <start-valid-time>2015-01-13T07:00:00-05:00</start-valid-time>. NB: that format is ISO 8601
                # EXCEPT for the ':' in the final time zone section (e.g., '-05:00'), so we remove it before parsing
                startValidTimeTrim = startValidTimeEle.text[:-3] + startValidTimeEle.text[-2:]
                dt = datetime.datetime.strptime(startValidTimeTrim, '%Y-%m-%dT%H:%M:%S%z')
                startValidTimes.append(dt)
            timeLayoutDict[layoutKey.text] = startValidTimes
        return timeLayoutDict


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


    #
    # calendar layout methods
    #


    def calendarHeaderRow(self):
        dayOfWeekNames = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        oldestHour = self.hours[0]
        newestHour = self.hours[-1]
        numDays = 1 + (newestHour.datetime - oldestHour.datetime).days
        weekday = oldestHour.datetime.weekday()
        headerRow = (dayOfWeekNames * 3)[weekday:weekday + numDays] # 3 is magic. at least good enough for 8 days of forecast data
        return headerRow
    
    
    def rowHeadingForHour(self, hourOfDay):
        """
        :param hourOfDay: 0 through 23
        :return: AM/PM version of hour
        """
        if hourOfDay < 13:
            return '{}'.format(hourOfDay)
        else:
            return '{}p'.format(hourOfDay - 12)


    def hoursAsCalendarRows(self):
        """
        Helper method used by views to lay out my hours in a calendar-like view.
        
        :return: Format: a list of 24 8-tuples containing day-of-the-week Hours. Conceptually returns a table where 
        there are 24 rows correspond to hours of the day (0 through 23), and 8 columns corresponding to the days of 
        the week. Each column is the Hour for that combination of hourOfDay and dayOfWeek. (Note that we have 8 
        columns and not 7 because a 7-day forecast will very likely 'overflow' into an eighth day. Not having 7 is OK 
        because the display is not a weekly calendar; it's a tabular display that's extended into the future as far 
        necessary. If 14 day forecasts become available then we will have 15 columns, and so forth.) To get a table 
        with no missing Hours, we have to interpolate from the most recently seen Hour, similar to what 
        hoursWithGapsFromXml() does.
        """
        # since we have my hours, which has no gaps, all we need to do is create missing Hours from the start of the 
        # first day (hour 0) to newest sampled hour - call them the head ones, and create missing Hours from the
        #  oldest sampled hour to the end of that last day (hour 23) - call them the tail
        oneHour = datetime.timedelta(hours=1)

        # create headMissingHours by working backward from the oldest hour to hour 0
        headMissingHours = []
        oldestHour = self.hours[0]

        currDatetime = oldestHour.datetime
        while currDatetime.hour != 0:
            currDatetime -= oneHour
            headMissingHours.append(Hour(currDatetime))
        headMissingHours.sort()
        
        # create tailMissingHours by working forward from the newest hour to hour 23
        tailMissingHours = []
        newestHour = self.hours[-1]
        
        currDatetime = newestHour.datetime
        while currDatetime.hour != 23:
            currDatetime += oneHour
            tailMissingHours.append(Hour(currDatetime))
        tailMissingHours.sort()

        # rows
        allHours = headMissingHours + self.hours + tailMissingHours
        numDays = 1 + (newestHour.datetime - oldestHour.datetime).days
        calendarRows = []
        for hourNum in range(24):           # calendar row
            hourRow = []
            for dayNum in range(numDays):   # calendar column
                hour = allHours[hourNum + (24 * dayNum)]
                hourRow.append(hour)
            calendarRows.append(hourRow)
        return calendarRows


    @staticmethod
    def isDaylightHour(hour):
        """
        :return: True if hour is a daylight hour. TODO: this is a very rough initial hack to limit hours shown. doesn't handle timezone, ...
        """
        return 7 < hour < 21
