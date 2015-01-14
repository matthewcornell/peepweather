import xml.etree.ElementTree as ET
import unittest

from Forecast import Forecast


class MyTestCase(unittest.TestCase):
    #
    # TODO: continue
    # back end: 01002 -> lat/lon -> .gov -> xml -> Hours
    # front end: /zip/01002 -> Forecast(01002) -> .getHours() -> layout using getDayOfWeek() and getHourOfDay()
    #

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.zipToLatLonName = {"01002": ("42.377651", "-72.50323", "Amherst, MA"),
                               "92105": ("32.741256", "-117.0951", "San Diego, CA")}


    def testForecastInstantiateLatLonName(self):
        for zipcode, (lat, lon, name) in self.zipToLatLonName.items():
            forecast = Forecast(zipcode)
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
            forecast = Forecast(zipcode)
            self.assertEqual(expURL, forecast.weatherDotGovUrl())


    def testXmlToHours(self):
        elementTree = ET.parse('test/test-forecast-data.xml')
        dwmlElement = elementTree.getroot()
        hours = Forecast.hoursForDwmlXmlRoot(dwmlElement)
        self.assertEqual(8, len(hours))
        # TODO check each Hour


    def testHours(self):
        # insert mock for test-forcast-data.xml then make sure getHours() returns same as testXmlToHours()
        self.fail()


    def testGetHour(self):
        self.fail()


    def testSummary(self):
        self.fail()


    def testHourToColor(self):
        self.fail()
