import xml.etree.ElementTree as ET
import unittest
import datetime
import operator
from unittest.mock import patch
import functools

from forecast.WeatherGovSource import WeatherGovSource
from forecast.Forecast import Forecast
from forecast.Location import Location
from forecast.Hour import Hour


class WeatherGovSourceTestCase(unittest.TestCase):
    """
    """


    def testErrorResponseFromAPI(self):
        elementTree = ET.parse('test/test-forecast-error-response.xml')
        expErrorXml = '<pre>\n        <problem>No data were found using the following input:</problem>\n        <product>time-series</product>\n        <startTime>2015-01-14T18:13:00</startTime>\n        <endTime>2017-01-15T18:13:00</endTime>\n        <Unit>e</Unit>\n        <latitudeLongitudes>\n            24.859832,-168.021815\n        </latitudeLongitudes>\n        <NDFDparameters>\n            temp pop12 wspd\n        </NDFDparameters>\n    </pre>\n'
        with self.assertRaisesRegex(ValueError, expErrorXml):
            location = Location('01002')
            WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)


    def testXmlToTimeLayoutDict(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        timeLayoutDict = WeatherGovSource.timeLayoutDictFromXml(dwmlElement)
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
        paramDict = WeatherGovSource.parameterDictFromXml(dwmlElement)
        self.assertEqual(expDict, paramDict)


    def testXmlToParamSamples(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        expDict = self.expDict_testXmlToParamSamples()
        paramSamplesDict = WeatherGovSource.parameterSamplesDictFromXml(dwmlElement)
        self.assertEqual(expDict, paramSamplesDict)


    def testXmlToParamSamplesSkyCover(self):
        elementTree = ET.parse('test/test-forecast-data-sky-cover.xml')
        dwmlElement = elementTree.getroot()
        expDict = self.expDict_testXmlToParamSamplesSkyCover()
        paramSamplesDict = WeatherGovSource.parameterSamplesDictFromXml(dwmlElement)
        self.assertEqual(expDict, paramSamplesDict)


    def testHourInstanceVariablesInclCloudiness(self):
        elementTree = ET.parse('test/test-forecast-data-sky-cover.xml')
        location = Location('01002')
        wgSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
        expCloudsDatetime = [
            (100, datetime.datetime(2015, 1, 27, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (99, datetime.datetime(2015, 1, 27, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (98, datetime.datetime(2015, 1, 27, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (96, datetime.datetime(2015, 1, 28, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (89, datetime.datetime(2015, 1, 28, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (82, datetime.datetime(2015, 1, 28, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (67, datetime.datetime(2015, 1, 28, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (53, datetime.datetime(2015, 1, 28, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (32, datetime.datetime(2015, 1, 28, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (9, datetime.datetime(2015, 1, 28, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (15, datetime.datetime(2015, 1, 28, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (14, datetime.datetime(2015, 1, 29, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (17, datetime.datetime(2015, 1, 29, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (20, datetime.datetime(2015, 1, 29, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (42, datetime.datetime(2015, 1, 29, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (65, datetime.datetime(2015, 1, 29, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (74, datetime.datetime(2015, 1, 29, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (84, datetime.datetime(2015, 1, 29, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (96, datetime.datetime(2015, 1, 30, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (96, datetime.datetime(2015, 1, 30, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (76, datetime.datetime(2015, 1, 30, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (65, datetime.datetime(2015, 1, 30, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (38, datetime.datetime(2015, 1, 31, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (28, datetime.datetime(2015, 1, 31, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (30, datetime.datetime(2015, 1, 31, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (28, datetime.datetime(2015, 1, 31, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (51, datetime.datetime(2015, 2, 1, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (56, datetime.datetime(2015, 2, 1, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (63, datetime.datetime(2015, 2, 1, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (63, datetime.datetime(2015, 2, 1, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (69, datetime.datetime(2015, 2, 2, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (67, datetime.datetime(2015, 2, 2, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (48, datetime.datetime(2015, 2, 2, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
            (63, datetime.datetime(2015, 2, 2, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))]
        for expClouds, expDatetime in expCloudsDatetime:
            foundHour = wgSource.findHourForDatetime(expDatetime)
            self.assertEqual(expClouds, foundHour.clouds)


    def testHoursWithGapsFromXml(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        expHoursWithGaps = self.expHoursWithGaps_testHoursWithGapsFromXml()
        actHoursWithGaps = WeatherGovSource.hoursWithGapsFromXml(dwmlElement, Forecast.PARAM_RANGE_STEPS_DEFAULT)
        self.assertEqual(expHoursWithGaps, actHoursWithGaps)


    def testHoursWithNoGaps(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        actHoursWithNoGaps = WeatherGovSource.hoursWithNoGapsFromXml(dwmlElement, Forecast.PARAM_RANGE_STEPS_DEFAULT)

        # test every hour is represented from oldest to newest with no gaps, ignoring weather values
        oneHour = datetime.timedelta(hours=1)
        oldestDatetime = actHoursWithNoGaps[0].datetime
        newestDatetime = actHoursWithNoGaps[-1].datetime

        expHoursWithNoGaps = []  # will not include weather valuess, just the correct on-the-hour datetime
        currDatetime = oldestDatetime
        while currDatetime <= newestDatetime:
            expHoursWithNoGaps.append(Hour(currDatetime))
            currDatetime += oneHour
        self.assertTrue(len(expHoursWithNoGaps), len(actHoursWithNoGaps))

        for (expHour, actHour) in zip(expHoursWithNoGaps, actHoursWithNoGaps):
            self.assertEqual(expHour.datetime, actHour.datetime)

        # spot-check some interpolated weather values
        h0 = Hour(datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 10,
                  3, -1)
        h1 = self.copyOfHourPlusOne(h0)
        h2 = self.copyOfHourPlusOne(h1)
        h3 = Hour(datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 6,
                  3, -1)
        self.assertEqual([h0, h1, h2, h3], actHoursWithNoGaps[:4])

        h0 = Hour(datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 19,
                  3, -1)
        h1 = self.copyOfHourPlusOne(h0)
        h2 = self.copyOfHourPlusOne(h1)
        h3 = Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 17,
                  3, -1)
        exph0Idx = 51
        self.assertEqual([h0, h1, h2, h3], actHoursWithNoGaps[exph0Idx:exph0Idx + 4])

        h0 = Hour(datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11,
                  28, 1, -1)
        h1 = self.copyOfHourPlusOne(h0)
        h2 = self.copyOfHourPlusOne(h1)
        h3 = self.copyOfHourPlusOne(h2)
        h4 = self.copyOfHourPlusOne(h3)
        h5 = self.copyOfHourPlusOne(h4)
        h6 = Hour(datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11,
                  23, 1, -1)
        exph0Idx = 162
        self.assertEqual([h0, h1, h2, h3, h4, h5, h6], actHoursWithNoGaps[exph0Idx:exph0Idx + 7])


    def testCloudsNone(self):
        elementTree = ET.parse('test/test-clouds-none.xml')
        dwmlElement = elementTree.getroot()
        actHoursWithGaps = WeatherGovSource.hoursWithGapsFromXml(dwmlElement, Forecast.PARAM_RANGE_STEPS_DEFAULT)
        for hour in actHoursWithGaps:
            self.assertIsNotNone(hour.clouds)


    @patch('forecast.Forecast.WeatherGovSource')
    def testCalendarHeaderRow(self, MockWeatherGovSource):
        location = Location('01002')
        elementTree = ET.parse('test/test-forecast-data.xml')
        testWGSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
        MockWeatherGovSource.return_value = testWGSource
        calendarHeader = Forecast(location).calendarHeaderRow()
        self.assertEqual(['T', 'W', 'T', 'F', 'S', 'S', 'M', 'T'], calendarHeader)

        MockWeatherGovSource.reset_mock()
        elementTree = ET.parse('test/test-forecast-only-seven-days.xml')
        testWGSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
        MockWeatherGovSource.return_value = testWGSource
        calendarHeader = Forecast(location).calendarHeaderRow()
        self.assertEqual(['S', 'S', 'M', 'T', 'W', 'T', 'F'], calendarHeader)


    @patch('forecast.Forecast.WeatherGovSource')
    def testHoursAsCalendarRows(self, MockWeatherGovSource):
        location = Location('01002')
        elementTree = ET.parse('test/test-forecast-data.xml')
        testWGSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
        MockWeatherGovSource.return_value = testWGSource
        actCalendarRows = Forecast(location).hoursAsCalendarRows()

        # test structure
        self.assertEqual(24, len(actCalendarRows))  # one row for each hour of the day
        for hourOfDayRow in actCalendarRows:
            self.assertEqual(8, len(hourOfDayRow))

        # flatten the table and compare to hours with no gaps. the first 18 and the last 4 are missing Hours
        hoursWithNoGaps = testWGSource.hours
        flattenedCalendarsHours = list(functools.reduce(operator.add, actCalendarRows))
        flattenedCalendarsHours.sort()
        self.assertEqual(hoursWithNoGaps, flattenedCalendarsHours[19:-4])
        self.assertTrue(all(map(lambda hour: hour.precip is None, flattenedCalendarsHours[:19])))
        self.assertTrue(all(map(lambda hour: hour.precip is None, flattenedCalendarsHours[-4:])))

        # spot check a few rows
        expRow1 = [
            Hour(datetime.datetime(2015, 1, 13, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), None,
                 None, None),
            Hour(datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 3, 2,
                 -1),
            Hour(datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 13,
                 2, -1),
            Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 17,
                 3, -1),
            Hour(datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 11,
                 4, -1),
            Hour(datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 9, 21,
                 5, -1),
            Hour(datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 28,
                 4, -1),
            Hour(datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 18,
                 3, -1)]
        self.assertEqual(expRow1, actCalendarRows[1])


    @patch('forecast.Forecast.WeatherGovSource')
    def testHoursAsCalendarRowsStructure(self, MockWeatherGovSource):
        fileRowCount = {'test/test-forecast-data.xml': 8, 'test/test-forecast-only-seven-days.xml': 7}
        for xmlFileName, expRowCount in fileRowCount.items():
            location = Location('01002')
            elementTree = ET.parse(xmlFileName)
            testWGSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
            MockWeatherGovSource.return_value = testWGSource

            actCaledarRows = Forecast(location).hoursAsCalendarRows()
            self.assertEqual(24, len(actCaledarRows))
            for hourOfDayRow in actCaledarRows:
                self.assertEqual(expRowCount, len(hourOfDayRow))


    @patch('forecast.Forecast.WeatherGovSource')
    def testHoursAsCalendarRowsIndexOutOfBounds(self, MockWeatherGovSource):
        location = Location('01002')
        elementTree = ET.parse('test/test-list-index-out-of-bounds.xml')
        testWGSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
        MockWeatherGovSource.return_value = testWGSource

        # this used to raise IndexError: list index out of range:
        actCaledarRows = Forecast(location).hoursAsCalendarRows()

        # also test for normalized hours:
        hour0Tz = actCaledarRows[0][0].datetime.tzinfo
        for hourOfDayRow in actCaledarRows:
            for hour in hourOfDayRow:
                self.assertEqual(hour.datetime.tzinfo, hour0Tz)


    # ==== support methods and long test data ====

    def copyOfHourPlusOne(self, hour):
        oneHour = datetime.timedelta(hours=1)
        return Hour(hour.datetime + oneHour, hour.precip, hour.temp, hour.wind, hour.clouds)


    def expHoursWithGaps_testHoursWithGapsFromXml(self):
        expHoursWithGaps = [
            Hour(datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 10,
                 3),
            Hour(datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 6,
                 3),
            Hour(datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 3,
                 2),
            Hour(datetime.datetime(2015, 1, 14, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 2,
                 2),
            Hour(datetime.datetime(2015, 1, 14, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 0,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 10,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 22,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 21,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 17,
                 1),
            Hour(datetime.datetime(2015, 1, 14, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 15,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 13,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 11,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 8,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 17,
                 1),
            Hour(datetime.datetime(2015, 1, 15, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 26,
                 1),
            Hour(datetime.datetime(2015, 1, 15, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 27,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 22,
                 2),
            Hour(datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 19,
                 3),
            Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 17,
                 3),
            Hour(datetime.datetime(2015, 1, 16, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 16,
                 4),
            Hour(datetime.datetime(2015, 1, 16, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 15,
                 4),
            Hour(datetime.datetime(2015, 1, 16, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 21,
                 6),
            Hour(datetime.datetime(2015, 1, 16, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 28,
                 7),
            Hour(datetime.datetime(2015, 1, 16, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 26,
                 7),
            Hour(datetime.datetime(2015, 1, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 19,
                 6),
            Hour(datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 11,
                 4),
            Hour(datetime.datetime(2015, 1, 17, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 6,
                 3),
            Hour(datetime.datetime(2015, 1, 17, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 24,
                 2),
            Hour(datetime.datetime(2015, 1, 17, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 9, 23,
                 4),
            Hour(datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 9, 21,
                 5),
            Hour(datetime.datetime(2015, 1, 18, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 21,
                 4),
            Hour(datetime.datetime(2015, 1, 18, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 38,
                 4),
            Hour(datetime.datetime(2015, 1, 18, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 33,
                 3),
            Hour(datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 28,
                 4),
            Hour(datetime.datetime(2015, 1, 19, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 24,
                 5),
            Hour(datetime.datetime(2015, 1, 19, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 32,
                 6),
            Hour(datetime.datetime(2015, 1, 19, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 24,
                 4),
            Hour(datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 18,
                 3),
            Hour(datetime.datetime(2015, 1, 20, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 14,
                 2),
            Hour(datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 28,
                 1),
            Hour(datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 23,
                 1)
        ]
        return expHoursWithGaps


    def expDict_testXmlToParamSamples(self):
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
        return expDict


    def expDict_testXmlToParamSamplesSkyCover(self):
        expDict = {
            'probability-of-precipitation': [
                (100, datetime.datetime(2015, 1, 27, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (33, datetime.datetime(2015, 1, 27, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (9, datetime.datetime(2015, 1, 28, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 28, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (17, datetime.datetime(2015, 1, 29, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (59, datetime.datetime(2015, 1, 29, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (56, datetime.datetime(2015, 1, 30, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (13, datetime.datetime(2015, 1, 30, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 31, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 31, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (23, datetime.datetime(2015, 2, 1, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (29, datetime.datetime(2015, 2, 1, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (22, datetime.datetime(2015, 2, 2, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))],
            'temperature': [
                (5, datetime.datetime(2015, 1, 27, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 27, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (-1, datetime.datetime(2015, 1, 27, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (0, datetime.datetime(2015, 1, 28, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (-1, datetime.datetime(2015, 1, 28, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (-2, datetime.datetime(2015, 1, 28, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 28, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 28, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 28, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 28, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (8, datetime.datetime(2015, 1, 28, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 29, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 29, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 29, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 29, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (19, datetime.datetime(2015, 1, 29, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (22, datetime.datetime(2015, 1, 29, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (19, datetime.datetime(2015, 1, 29, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (17, datetime.datetime(2015, 1, 30, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (27, datetime.datetime(2015, 1, 30, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (24, datetime.datetime(2015, 1, 30, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 30, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (-7, datetime.datetime(2015, 1, 31, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (-16, datetime.datetime(2015, 1, 31, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 31, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 31, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 2, 1, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (0, datetime.datetime(2015, 2, 1, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (13, datetime.datetime(2015, 2, 1, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (9, datetime.datetime(2015, 2, 1, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (10, datetime.datetime(2015, 2, 2, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 2, 2, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 2, 2, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 2, 2, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))],
            'wind-speed': [
                (13, datetime.datetime(2015, 1, 27, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (13, datetime.datetime(2015, 1, 27, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (10, datetime.datetime(2015, 1, 27, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 28, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 28, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 28, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 28, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 28, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 28, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 28, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 28, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 29, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 29, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (2, datetime.datetime(2015, 1, 29, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 1, 29, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 29, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 29, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 1, 29, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 1, 30, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (1, datetime.datetime(2015, 1, 30, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (6, datetime.datetime(2015, 1, 30, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (12, datetime.datetime(2015, 1, 30, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 31, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (12, datetime.datetime(2015, 1, 31, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (11, datetime.datetime(2015, 1, 31, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (7, datetime.datetime(2015, 1, 31, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 2, 1, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 2, 1, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 2, 1, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (4, datetime.datetime(2015, 2, 1, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 2, 2, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (3, datetime.datetime(2015, 2, 2, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 2, 2, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (5, datetime.datetime(2015, 2, 2, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))],
            'cloud-amount': [
                (100, datetime.datetime(2015, 1, 27, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (99, datetime.datetime(2015, 1, 27, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (98, datetime.datetime(2015, 1, 27, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (96, datetime.datetime(2015, 1, 28, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (89, datetime.datetime(2015, 1, 28, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (82, datetime.datetime(2015, 1, 28, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (67, datetime.datetime(2015, 1, 28, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (53, datetime.datetime(2015, 1, 28, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (32, datetime.datetime(2015, 1, 28, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (9, datetime.datetime(2015, 1, 28, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (15, datetime.datetime(2015, 1, 28, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (14, datetime.datetime(2015, 1, 29, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (17, datetime.datetime(2015, 1, 29, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (20, datetime.datetime(2015, 1, 29, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (42, datetime.datetime(2015, 1, 29, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (65, datetime.datetime(2015, 1, 29, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (74, datetime.datetime(2015, 1, 29, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (84, datetime.datetime(2015, 1, 29, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (96, datetime.datetime(2015, 1, 30, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (96, datetime.datetime(2015, 1, 30, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (76, datetime.datetime(2015, 1, 30, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (65, datetime.datetime(2015, 1, 30, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (38, datetime.datetime(2015, 1, 31, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (28, datetime.datetime(2015, 1, 31, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (30, datetime.datetime(2015, 1, 31, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (28, datetime.datetime(2015, 1, 31, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (51, datetime.datetime(2015, 2, 1, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (56, datetime.datetime(2015, 2, 1, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (63, datetime.datetime(2015, 2, 1, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (63, datetime.datetime(2015, 2, 1, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (69, datetime.datetime(2015, 2, 2, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (67, datetime.datetime(2015, 2, 2, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (48, datetime.datetime(2015, 2, 2, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))),
                (63, datetime.datetime(2015, 2, 2, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))))]
        }
        return expDict
