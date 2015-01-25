import functools
import xml.etree.ElementTree as ET
import unittest
import datetime
import operator

from forecast.Forecast import Forecast
from forecast.Hour import Hour


class MyTestCase(unittest.TestCase):
    def testForecastConstructorArg(self):
        elementTree = ET.parse('test/test-forecast-data.xml')

        # zip good: has an entry in the csv file
        Forecast('01002', elementTree=elementTree)  # does not raise

        # zip bad: not in csv
        with self.assertRaisesRegex(ValueError, "couldn't find zipcode: 99999"):
            Forecast('99999', elementTree=elementTree)

        # zip bad: None
        with self.assertRaisesRegex(ValueError, 'invalid zipOrLatLon'):
            Forecast(None, elementTree=elementTree)

        # latLon good: valid format
        Forecast(['42.375370', '-72.519249'], elementTree=elementTree)  # does not raise

        # latLon bad: invalid formats
        for zipOrLatLon in [[]], [None], ['42.375370', None], [1, '-72.519249']:
            with self.assertRaisesRegex(ValueError, 'invalid zipOrLatLon'):
                Forecast(zipOrLatLon, elementTree=elementTree)
                
        # default rangeDict:
        forecast = Forecast('01002', elementTree=elementTree)
        self.assertEqual(Forecast.PARAM_RANGE_STEPS_DEFAULT, forecast.rangeDict)

        # custom rangeDict:
        rangeDict = {'precip': [0, 1],  # H-M-L
                     'temp': [2, 3, 4, 5],  # L-M-H-M-L
                     'wind': [6, 7],  # H-M-L
        }
        forecast = Forecast('01002', rangeDict=rangeDict, elementTree=elementTree)
        self.assertEqual(rangeDict, forecast.rangeDict)


    def testErrorResponseFromAPI(self):
        elementTree = ET.parse('test/test-forecast-error-response.xml')
        expErrorXml = '<pre>\n        <problem>No data were found using the following input:</problem>\n        <product>time-series</product>\n        <startTime>2015-01-14T18:13:00</startTime>\n        <endTime>2017-01-15T18:13:00</endTime>\n        <Unit>e</Unit>\n        <latitudeLongitudes>\n            24.859832,-168.021815\n        </latitudeLongitudes>\n        <NDFDparameters>\n            temp pop12 wspd\n        </NDFDparameters>\n    </pre>\n'
        with self.assertRaisesRegex(ValueError, expErrorXml):
            Forecast('01002', elementTree=elementTree)


    def testForecastInstantiateLatLonName(self):
        zipToLatLonName = {"01002": ("42.377651", "-72.50323", "Amherst, MA"),
                           "92105": ("32.741256", "-117.0951", "San Diego, CA")}
        elementTree = ET.parse('test/test-forecast-data.xml')
        for zipcode, (lat, lon, name) in zipToLatLonName.items():
            forecast = Forecast(zipcode, elementTree=elementTree)
            self.assertEqual(zipcode, forecast.zipcode)
            self.assertEqual((lat, lon), forecast.latLon)
            self.assertEqual(name, forecast.name)


    def testWeatherDotGovUrl(self):
        # test zipcode constructor
        elementTree = ET.parse('test/test-forecast-data.xml')
        zipToLatLon = {"01002": ("42.377651", "-72.50323"),
                       "92105": ("32.741256", "-117.0951")}
        for zipcode, (lat, lon) in zipToLatLon.items():
            expURL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php' \
                     '?whichClient=NDFDgen' \
                     '&lat={lat}' \
                     '&lon={lon}' \
                     '&product=time-series' \
                     '&Unit=e' \
                     '&temp=temp' \
                     '&pop12=pop12' \
                     '&wspd=wspd' \
                     '&Submit=Submit'.format(lat=lat, lon=lon)
            # test passing zipcode to constructor
            forecast = Forecast(zipcode, elementTree=elementTree)
            self.assertEqual(expURL, forecast.weatherDotGovUrl())

            # test passing latLon to constructor
            forecast = Forecast([lat, lon], elementTree=elementTree)
            self.assertEqual(expURL, forecast.weatherDotGovUrl())


    def testSearchZipcodes(self):
        query = 'barro'
        expZipNameLatLonTuples = [("54812", "Barron, WI", "45.39701", "-91.86337"),
                                  ("54813", "Barronett, WI", "45.646145", "-92.01923"),
                                  ("99723", "Barrow, AK", "71.299525", "-156.74891")]
        zipNameLatLonTuples = Forecast.searchZipcodes(query)
        self.assertListEqual(expZipNameLatLonTuples, zipNameLatLonTuples)


    def testXmlToTimeLayoutDict(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        timeLayoutDict = Forecast.timeLayoutDictFromXml(dwmlElement)
        self.assertEqual(2, len(timeLayoutDict))
        self.assertIn("k-p12h-n15-1", timeLayoutDict)
        self.assertIn("k-p3h-n41-2", timeLayoutDict)

        # check size and type of result, and spot check the first value
        tlP12 = timeLayoutDict["k-p12h-n15-1"]
        self.assertEqual(15, len(tlP12))
        self.assertTrue(all(map(lambda x: type(x) == datetime.datetime, tlP12)))
        self.assertEqual(datetime.datetime(2015, 1, 13, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                         tlP12[0])

        tlP3 = timeLayoutDict["k-p3h-n41-2"]
        self.assertEqual(41, len(tlP3))
        self.assertTrue(all(map(lambda x: type(x) == datetime.datetime, tlP3)))
        self.assertEqual(datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                         tlP3[0])


    def testXmlToParameterDict(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        expDict = {
            'temperature': ("k-p3h-n41-2",
                            [10, 6, 3, 2, 0, 10, 22, 21, 17, 15, 13, 11, 8, 17, 26, 27, 22, 19, 17, 16, 15, 21, 28, 26,
                             19, 11, 6, 24, 23, 21, 21, 38, 33, 28, 24, 32, 24, 18, 14, 28, 23]),
            'probability-of-precipitation': ("k-p12h-n15-1", [1, 0, 4, 11, 8, 5, 4, 3, 3, 9, 20, 20, 10, 10, 11]),
            'wind-speed': ("k-p3h-n41-2",
                           [3, 3, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 3, 3, 4, 4, 6, 7, 7, 6, 4, 3, 2, 4, 5, 4,
                            4, 3, 4, 5, 6, 4, 3, 2, 1, 1])
        }
        paramDict = Forecast.parameterDictFromXml(dwmlElement)
        self.assertEqual(expDict, paramDict)


    def testXmlToParamSamples(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        expDict = {
            'temperature': [
                (10, datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 14, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (0, datetime.datetime(2015, 1, 14, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (10, datetime.datetime(2015, 1, 14, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (22, datetime.datetime(2015, 1, 14, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (21, datetime.datetime(2015, 1, 14, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (17, datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (15, datetime.datetime(2015, 1, 14, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (13, datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 15, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (8, datetime.datetime(2015, 1, 15, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (17, datetime.datetime(2015, 1, 15, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (26, datetime.datetime(2015, 1, 15, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (27, datetime.datetime(2015, 1, 15, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (22, datetime.datetime(2015, 1, 15, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (19, datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (17, datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (16, datetime.datetime(2015, 1, 16, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (15, datetime.datetime(2015, 1, 16, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (21, datetime.datetime(2015, 1, 16, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (28, datetime.datetime(2015, 1, 16, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (26, datetime.datetime(2015, 1, 16, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (19, datetime.datetime(2015, 1, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 17, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (24, datetime.datetime(2015, 1, 17, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (23, datetime.datetime(2015, 1, 17, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (21, datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (21, datetime.datetime(2015, 1, 18, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (38, datetime.datetime(2015, 1, 18, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (33, datetime.datetime(2015, 1, 18, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (28, datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (24, datetime.datetime(2015, 1, 19, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (32, datetime.datetime(2015, 1, 19, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (24, datetime.datetime(2015, 1, 19, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (18, datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (14, datetime.datetime(2015, 1, 20, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (28, datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (23, datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))],
            'probability-of-precipitation': [
                (1, datetime.datetime(2015, 1, 13, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (0, datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 14, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (8, datetime.datetime(2015, 1, 15, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 15, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 16, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 17, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (9, datetime.datetime(2015, 1, 17, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (20, datetime.datetime(2015, 1, 18, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (20, datetime.datetime(2015, 1, 18, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (10, datetime.datetime(2015, 1, 19, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (10, datetime.datetime(2015, 1, 19, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 20, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))],
            'wind-speed': [
                (3, datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 14, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 14, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 14, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 14, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 14, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 14, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 15, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 15, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 15, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 15, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 15, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 15, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 16, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 16, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 16, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 16, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 16, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 17, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 17, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 17, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 18, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 18, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 18, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 19, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 19, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 19, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 20, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))]
        }
        paramSamplesDict = Forecast.parameterSamplesDictFromXml(dwmlElement)
        self.assertEqual(expDict, paramSamplesDict)


    def testHoursWithGapsFromXml(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        expHoursWithGaps = self.expectedHoursWithGaps()
        actHoursWithGaps = Forecast.hoursWithGapsFromXml(dwmlElement, Forecast.PARAM_RANGE_STEPS_DEFAULT)
        self.assertEqual(expHoursWithGaps, actHoursWithGaps)


    def testHoursWithNoGaps(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        actHoursWithNoGaps = Forecast.hoursWithNoGapsFromXml(dwmlElement, Forecast.PARAM_RANGE_STEPS_DEFAULT)

        # test every hour is represented from oldest to newest with no gaps, ignoring weather values
        oneHour = datetime.timedelta(hours=1)
        oldestDatetime = actHoursWithNoGaps[0].datetime
        newestDatetime = actHoursWithNoGaps[-1].datetime

        expHoursWithNoGaps = []  # will not include weather valuess, just the correct on-the-hour datetime
        currDatetime = oldestDatetime
        while currDatetime <= newestDatetime:
            expHoursWithNoGaps.append(Hour(currDatetime, Forecast.PARAM_RANGE_STEPS_DEFAULT))
            currDatetime += oneHour
        self.assertTrue(len(expHoursWithNoGaps), len(actHoursWithNoGaps))

        for (expHour, actHour) in zip(expHoursWithNoGaps, actHoursWithNoGaps):
            self.assertEqual(expHour.datetime, actHour.datetime)

        # spot-check some interpolated weather values
        h0 = Hour(datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 10, 3)
        h1 = self.copyOfHourPlusOne(h0)
        h2 = self.copyOfHourPlusOne(h1)
        h3 = Hour(datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 6, 3)
        self.assertEqual([h0, h1, h2, h3], actHoursWithNoGaps[:4])

        h0 = Hour(datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 19, 3)
        h1 = self.copyOfHourPlusOne(h0)
        h2 = self.copyOfHourPlusOne(h1)
        h3 = Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 17, 3)
        exph0Idx = 51
        self.assertEqual([h0, h1, h2, h3], actHoursWithNoGaps[exph0Idx:exph0Idx + 4])

        h0 = Hour(datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 28, 1)
        h1 = self.copyOfHourPlusOne(h0)
        h2 = self.copyOfHourPlusOne(h1)
        h3 = self.copyOfHourPlusOne(h2)
        h4 = self.copyOfHourPlusOne(h3)
        h5 = self.copyOfHourPlusOne(h4)
        h6 = Hour(datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 23, 1)
        exph0Idx = 162
        self.assertEqual([h0, h1, h2, h3, h4, h5, h6], actHoursWithNoGaps[exph0Idx:exph0Idx + 7])


    def testHours(self):
        # make sure hours with no gaps is saved in constructor
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        hoursWithNoGaps = Forecast.hoursWithNoGapsFromXml(dwmlElement, Forecast.PARAM_RANGE_STEPS_DEFAULT)
        forecast = Forecast('01002', elementTree=elementTree)
        self.assertEqual(hoursWithNoGaps, forecast.hours)


    def testColumnHeaderRow(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        forecast = Forecast('01002', elementTree=elementTree)
        calendarHeader = forecast.calendarHeaderRow()
        self.assertEqual(['T', 'W', 'T', 'F', 'S', 'S', 'M', 'T'], calendarHeader)

        elementTree = ET.parse('test/test-forecast-only-seven-days.xml')
        forecast = Forecast('01002', elementTree=elementTree)
        calendarHeader = forecast.calendarHeaderRow()
        self.assertEqual(['S', 'S', 'M', 'T', 'W', 'T', 'F'], calendarHeader)


    def testHoursAsCalendarRows(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        forecast = Forecast('01002', elementTree=elementTree)
        actCaledarRows = forecast.hoursAsCalendarRows()

        # test structure
        self.assertEqual(24, len(actCaledarRows))  # one row for each hour of the day
        for row in actCaledarRows:
            self.assertEqual(8, len(row))

        # flatten the table and compare to hours with no gaps. the first 18 and the last 4 are missing Hours
        hoursWithNoGaps = forecast.hours
        flattenedCaledarHours = list(functools.reduce(operator.add, actCaledarRows))
        flattenedCaledarHours.sort()
        self.assertEqual(hoursWithNoGaps, flattenedCaledarHours[19:-4])
        self.assertTrue(all(map(lambda hour: hour.precip is None, flattenedCaledarHours[:19])))
        self.assertTrue(all(map(lambda hour: hour.precip is None, flattenedCaledarHours[-4:])))

        # spot check a few rows
        expRow1 = [
            Hour(datetime.datetime(2015, 1, 13, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, None, None, None),
            Hour(datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 3, 2),
            Hour(datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 13, 2),
            Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 17, 3),
            Hour(datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 3, 11, 4),
            Hour(datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 9, 21, 5),
            Hour(datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 20, 28, 4),
            Hour(datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 10, 18, 3)]
        self.assertEqual(expRow1, actCaledarRows[1])


    def testHoursAsCalendarRowsStructure(self):
        fileRowCount = {'test/test-forecast-data.xml': 8, 'test/test-forecast-only-seven-days.xml': 7}
        for xmlFileName, expRowCount in fileRowCount.items():
            elementTree = ET.parse(xmlFileName)
            forecast = Forecast('01002', elementTree=elementTree)
            actCaledarRows = forecast.hoursAsCalendarRows()
            self.assertEqual(24, len(actCaledarRows))
            for row in actCaledarRows:
                self.assertEqual(expRowCount, len(row))


    def testIsDaylight(self):
        for hour in range(24):
            expIsDaylight = 7 < hour < 21
            self.assertEqual(expIsDaylight, Forecast.isDaylightHour(hour))


    def testHourColorDesirabilities(self):
        # recall steps:
        # 1. assign DESIRABILITY of each parameter into THREE categories:
        # P_DES_LOW, P_DES_MED, P_DES_HIGH
        #
        # 2. combine the three parameters' three desirabilities into an overall desirability in FOUR categories:
        # H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH
        #
        # 3. assign colors accordingly
        expParamValRatings = {
            'precip': [(0, Hour.P_DES_HIGH),
                       (9, Hour.P_DES_HIGH),
                       (10, Hour.P_DES_MED),
                       (29, Hour.P_DES_MED),
                       (30, Hour.P_DES_LOW),
                       (100, Hour.P_DES_LOW),
            ],
            'wind': [(0, Hour.P_DES_HIGH),
                     (7, Hour.P_DES_HIGH),
                     (8, Hour.P_DES_MED),
                     (11, Hour.P_DES_MED),
                     (12, Hour.P_DES_LOW),
                     (100, Hour.P_DES_LOW),
            ],
            'temp': [(-100, Hour.P_DES_LOW),
                     (31, Hour.P_DES_LOW),
                     (32, Hour.P_DES_MED),
                     (40, Hour.P_DES_MED),
                     (41, Hour.P_DES_HIGH),
                     (69, Hour.P_DES_HIGH),
                     (70, Hour.P_DES_MED),
                     (84, Hour.P_DES_MED),
                     (85, Hour.P_DES_LOW),
                     (100, Hour.P_DES_LOW),
            ],
        }
        for paramName, expParamValRatings in expParamValRatings.items():
            for paramval, expParamRating in expParamValRatings:
                hour = Hour(None, Forecast.PARAM_RANGE_STEPS_DEFAULT)
                self.assertEqual(expParamRating, hour.paramDesirabilityForValue(paramName, paramval))

        # check overall hour desirability. counts: Hour.P_DES_LOW, Hour.P_DES_MED, Hour.P_DES_HIGH
        pDesCountsDict = {(0, 1, 2): Hour.H_DES_LOW,
                          (2, 0, 1): Hour.H_DES_LOW,
                          (3, 0, 0): Hour.H_DES_LOW,
                          (0, 0, 3): Hour.H_DES_HIGH,
                          (0, 1, 2): Hour.H_DES_MED_HIGH,
                          (0, 2, 1): Hour.H_DES_MED_LOW,
        }
        for paramDesireTuple, expHourDesire in pDesCountsDict.items():
            self.assertEqual(expHourDesire, Hour.hourDesirabilityForParamDesCounts(*paramDesireTuple))

        with self.assertRaisesRegex(ValueError, "counts weren't all numbers"):
            Hour.hourDesirabilityForParamDesCounts(None, 0, 0)

        with self.assertRaisesRegex(ValueError, "counts didn't add to 3"):
            Hour.hourDesirabilityForParamDesCounts(2, 2, 2)


    def testHourColor(self):
        self.assertEqual(Hour.HOUR_DESIRABILITY_TO_COLOR[Hour.H_DES_LOW], Hour.colorForHourDesirability(Hour.H_DES_LOW))
        self.assertEqual(Hour.HOUR_DESIRABILITY_TO_COLOR[Hour.H_DES_MED_LOW],
                         Hour.colorForHourDesirability(Hour.H_DES_MED_LOW))
        self.assertEqual(Hour.HOUR_DESIRABILITY_TO_COLOR[Hour.H_DES_MED_HIGH],
                         Hour.colorForHourDesirability(Hour.H_DES_MED_HIGH))
        self.assertEqual(Hour.HOUR_DESIRABILITY_TO_COLOR[Hour.H_DES_HIGH],
                         Hour.colorForHourDesirability(Hour.H_DES_HIGH))

        # finally, test color()! tuple: (precip, temp, wind)
        paramToColorDict = {(100, 65, 0): Hour.colorForHourDesirability(Hour.H_DES_LOW),  # precip low
                            (20, 40, 0): Hour.colorForHourDesirability(Hour.H_DES_MED_LOW),
                            # precip med, temp med, wind high
                            (20, 65, 0): Hour.colorForHourDesirability(Hour.H_DES_MED_HIGH),
                            # precip med, temp high, wind high
                            (0, 65, 0): Hour.colorForHourDesirability(Hour.H_DES_HIGH),  # all high
        }
        for precipTempWindTuple, expColor in paramToColorDict.items():
            hour = Hour(None, Forecast.PARAM_RANGE_STEPS_DEFAULT, *precipTempWindTuple)
            self.assertEqual(expColor, hour.color())


    def expectedHoursWithGaps(self):
        # return expected output for Forecast.hoursWithGapsFromXml()
        expHoursWithGaps = [
            Hour(datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 10,
                 3),
            Hour(datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 6,
                 3),
            Hour(datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 3,
                 2),
            Hour(datetime.datetime(2015, 1, 14, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 2,
                 2),
            Hour(datetime.datetime(2015, 1, 14, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 0,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 10,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 22,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 21,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 17,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 15,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 13,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 11,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 8, 8,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 8, 17,
                 1),
            Hour(datetime.datetime(2015, 1, 15, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 8, 26,
                 1),
            Hour(datetime.datetime(2015, 1, 15, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 8, 27,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 22,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 19,
                 3),
            Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 17,
                 3),
            Hour(datetime.datetime(2015, 1, 16, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 5, 16,
                 4),
            Hour(datetime.datetime(2015, 1, 16, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 15,
                 4),
            Hour(datetime.datetime(2015, 1, 16, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 21,
                 6),
            Hour(datetime.datetime(2015, 1, 16, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 28,
                 7),
            Hour(datetime.datetime(2015, 1, 16, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 4, 26,
                 7),
            Hour(datetime.datetime(2015, 1, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 3, 19,
                 6),
            Hour(datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 3, 11,
                 4),
            Hour(datetime.datetime(2015, 1, 17, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 3, 6,
                 3),
            Hour(datetime.datetime(2015, 1, 17, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 3, 24,
                 2),
            Hour(datetime.datetime(2015, 1, 17, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 9, 23,
                 4),
            Hour(datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 9, 21,
                 5),
            Hour(datetime.datetime(2015, 1, 18, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 20, 21,
                 4),
            Hour(datetime.datetime(2015, 1, 18, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 20, 38,
                 4),
            Hour(datetime.datetime(2015, 1, 18, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 20, 33,
                 3),
            Hour(datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 20, 28,
                 4),
            Hour(datetime.datetime(2015, 1, 19, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 10, 24,
                 5),
            Hour(datetime.datetime(2015, 1, 19, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 10, 32,
                 6),
            Hour(datetime.datetime(2015, 1, 19, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 10, 24,
                 4),
            Hour(datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 10, 18,
                 3),
            Hour(datetime.datetime(2015, 1, 20, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 14,
                 2),
            Hour(datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 28,
                 1),
            Hour(datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                 Forecast.PARAM_RANGE_STEPS_DEFAULT, 11, 23,
                 1)
        ]
        return expHoursWithGaps


    def copyOfHourPlusOne(self, hour):
        oneHour = datetime.timedelta(hours=1)
        return Hour(hour.datetime + oneHour, Forecast.PARAM_RANGE_STEPS_DEFAULT, hour.precip, hour.temp, hour.wind)
