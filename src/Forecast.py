import csv
from datetime import datetime


class Forecast:
    #
    # TODO preload zipcode-clean.csv into memory
    #

    def __init__(self, zipcode):
        (lat, lon, name) = self.latLonNameForZipcode(zipcode)
        self.zipcode = zipcode
        self.latLon = (lat, lon)
        self.name = name


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


    @staticmethod
    def latLonNameForZipcode(zipcode):
        """
        :param zipcode:
        :return: looks up and returns information for zipcode as a 3-tuple of the form:
        (latitude, longitude, name)
        """
        # zipcode-clean.csv: "zip","city","state","latitude","longitude","timezone","dst"
        with open('src/zipcode-clean.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for (csv_zipcode, city, state, latitude, longitude, timezone, dst) in csvreader:
                if csv_zipcode == zipcode:
                    return latitude, longitude, city + ", " + state
        raise ValueError("invalid zipcode: {}".format(zipcode))


    #
    # hoursFromDwmlXmlRoot() and friends
    #


    @classmethod
    def hoursFromDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: a sequence of Hour instances corresponding to the passed DWML document element
        """
        hours = []

        # TODO. self.timeLayoutDictFromDwmlXmlRoot(dwmlElement), self.parameterDictFromDwmlXmlRoot(), etc.

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
                #  EXCEPT for the ':' in the final time zone section (e.g., '-05:00'), so we remove it before parsing
                startValidTimeTrim = startValidTimeEle.text[:-3] + startValidTimeEle.text[-2:]
                dt = datetime.strptime(startValidTimeTrim, '%Y-%m-%dT%H:%M:%S%z')
                startValidTimes.append(dt)
            timeLayoutDict[layoutKey.text] = startValidTimes
        return timeLayoutDict


    @classmethod
    def parameterDictFromDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: dict: {<name> -> (<time-layout>, [int values])}
        
        <parameters applicable-location="point1">
            <temperature type="hourly" units="Fahrenheit" time-layout="k-p3h-n41-2">
                <name>Temperature</name>
                <value>10</value>
                ...
            <wind-speed type="sustained" units="knots" time-layout="k-p3h-n41-2">
                <name>Wind Speed</name>
                <value>3</value>
                ...
            <probability-of-precipitation type="12 hour" units="percent" time-layout="k-p12h-n15-1">
                <name>12 Hourly Probability of Precipitation</name>
                <value>1</value>
                ...

        """
        paramDict = {}
        for paramEle in dwmlElement.find('data/parameters'):
            paramVals = list(map(lambda val: int(val.text), paramEle.findall('value')))
            timeLayout = paramEle.attrib['time-layout']
            paramDict[paramEle.tag] = (timeLayout, paramVals)
        return paramDict
    