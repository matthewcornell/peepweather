import xml.etree.ElementTree as ET
import unittest
import datetime

from forecast.Forecast import Forecast
from forecast.Hour import Hour


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.zipToLatLonName = {"01002": ("42.377651", "-72.50323", "Amherst, MA"),
                               "92105": ("32.741256", "-117.0951", "San Diego, CA")}


    def testForecastInstantiateLatLonName(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        for zipcode, (lat, lon, name) in self.zipToLatLonName.items():
            forecast = Forecast(zipcode, elementTree)
            self.assertEqual(zipcode, forecast.zipcode)
            self.assertEqual((lat, lon), forecast.latLon)
            self.assertEqual(name, forecast.name)

        with self.assertRaisesRegex(ValueError, 'invalid zipcode: None'):
            Forecast(None)


    def testWeatherDotGovUrl(self):
        for zipcode, (lat, lon, name) in self.zipToLatLonName.items():
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
            elementTree = ET.parse('test/test-forecast-data.xml')
            forecast = Forecast(zipcode, elementTree)
            self.assertEqual(expURL, forecast.weatherDotGovUrl())


    def testXmlToTimeLayoutDict(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        timeLayoutDict = Forecast.timeLayoutDictFromDwmlXmlRoot(dwmlElement)
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
        paramDict = Forecast.parameterDictFromDwmlXmlRoot(dwmlElement)
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
        paramSamplesDict = Forecast.parameterSamplesDictFromDwmlXmlRoot(dwmlElement)
        self.assertEqual(expDict, paramSamplesDict)


    def testXmlToHours(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        expHoursWithGaps = [
            Hour(datetime.datetime(2015, 1, 13, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 10, 3),
            Hour(datetime.datetime(2015, 1, 13, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 6, 3),
            Hour(datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 3, 2),
            Hour(datetime.datetime(2015, 1, 14, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 0, 2, 2),
            Hour(datetime.datetime(2015, 1, 14, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 0, 1),
            Hour(datetime.datetime(2015, 1, 14, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 10, 1),
            Hour(datetime.datetime(2015, 1, 14, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 22, 1),
            Hour(datetime.datetime(2015, 1, 14, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 21, 1),
            Hour(datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 17, 1),
            Hour(datetime.datetime(2015, 1, 14, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 15, 2),
            Hour(datetime.datetime(2015, 1, 15, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 13, 2),
            Hour(datetime.datetime(2015, 1, 15, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 11, 2),
            Hour(datetime.datetime(2015, 1, 15, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 8, 2),
            Hour(datetime.datetime(2015, 1, 15, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 17, 1),
            Hour(datetime.datetime(2015, 1, 15, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 26, 1),
            Hour(datetime.datetime(2015, 1, 15, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 8, 27, 2),
            Hour(datetime.datetime(2015, 1, 15, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 22, 2),
            Hour(datetime.datetime(2015, 1, 15, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 19, 3),
            Hour(datetime.datetime(2015, 1, 16, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 17, 3),
            Hour(datetime.datetime(2015, 1, 16, 4, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 5, 16, 4),
            Hour(datetime.datetime(2015, 1, 16, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 15, 4),
            Hour(datetime.datetime(2015, 1, 16, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 21, 6),
            Hour(datetime.datetime(2015, 1, 16, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 28, 7),
            Hour(datetime.datetime(2015, 1, 16, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 4, 26, 7),
            Hour(datetime.datetime(2015, 1, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 19, 6),
            Hour(datetime.datetime(2015, 1, 17, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 11, 4),
            Hour(datetime.datetime(2015, 1, 17, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 6, 3),
            Hour(datetime.datetime(2015, 1, 17, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 3, 24, 2),
            Hour(datetime.datetime(2015, 1, 17, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 9, 23, 4),
            Hour(datetime.datetime(2015, 1, 18, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 9, 21, 5),
            Hour(datetime.datetime(2015, 1, 18, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 21, 4),
            Hour(datetime.datetime(2015, 1, 18, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 38, 4),
            Hour(datetime.datetime(2015, 1, 18, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 33, 3),
            Hour(datetime.datetime(2015, 1, 19, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 20, 28, 4),
            Hour(datetime.datetime(2015, 1, 19, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 24, 5),
            Hour(datetime.datetime(2015, 1, 19, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 32, 6),
            Hour(datetime.datetime(2015, 1, 19, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 24, 4),
            Hour(datetime.datetime(2015, 1, 20, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 10, 18, 3),
            Hour(datetime.datetime(2015, 1, 20, 7, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 14, 2),
            Hour(datetime.datetime(2015, 1, 20, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 28, 1),
            Hour(datetime.datetime(2015, 1, 20, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 23, 1)
        ]
        hoursWithGaps = Forecast.hoursFromDwmlXmlRoot(dwmlElement)
        self.assertEqual(expHoursWithGaps, hoursWithGaps)


    def testSearchZipcodes(self):
        query = 'barro'
        expZipNameTuples = [("54812", "Barron, WI"), ("54813", "Barronett, WI"), ("99723", "Barrow, AK")]
        zipNameTuples = Forecast.searchZipcodes(query)
        self.assertListEqual(expZipNameTuples, zipNameTuples)


    def testBadZip(self):
        # test 1/2: valid input. patch constructor:
        elementTree = ET.parse('test/test-forecast-data.xml')
        forecast = Forecast('01002', elementTree)
        self.assertFalse(forecast.error)

        # test 2/2: error input. patch constructor:
        elementTree = ET.parse('test/test-forecast-error-response.xml')
        forecast = Forecast('01002', elementTree)
        expErrorStr = '<pre>\n        <problem>No data were found using the following input:</problem>\n        <product>time-series</product>\n        <startTime>2015-01-14T18:13:00</startTime>\n        <endTime>2017-01-15T18:13:00</endTime>\n        <Unit>e</Unit>\n        <latitudeLongitudes>\n            24.859832,-168.021815\n        </latitudeLongitudes>\n        <NDFDparameters>\n            temp pop12 wspd\n        </NDFDparameters>\n    </pre>\n'
        self.assertEqual(expErrorStr, forecast.error)
        
    
    def testGetHour(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        forecast = Forecast('01002', elementTree)
        expHour = Hour(datetime.datetime(2015, 1, 14, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))), 11, 17, 1)   # 'Tue, 01/13, 07:00 PM'
        hour = forecast.getHour(expHour.datetime.weekday(), expHour.datetime.hour)
        self.assertEqual(expHour, hour)
        
        # now test that getHour() fills in gaps

        # {% for hourOfDay in HOUR_OF_DAY_RANGE %}            {# each row is an hour of day #}
        # <tr>
        # <th style="background-color:white;">{{ hourOfDay }}</th>
        # {% for dayOfWeek in DAY_OF_WEEK_RANGE %}    {# each column is a day of week #}
        # {% set hour = forecast.getHour(dayOfWeek, hourOfDay) %}

        self.fail()


    def testForecastSummary(self):
        self.fail()


    def testHourColor(self):
        self.fail()
