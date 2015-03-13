import unittest

from forecast.Location import Location, ZipCodeLocation
from forecast.ZipcodeUtil import latLonNameForZipcode
from forecast.ZipcodeUtil import searchZipcodes


class LocationTestCase(unittest.TestCase):
    """
    """


    def testPlainLocation(self):
        latLon = ['42.377651', '-72.50323']
        for latLonPair in [(None, None), (latLon[0], None), (None, latLon[1])]:
            with self.assertRaisesRegex(ValueError, "invalid format for latitude or longitude: None"):
                Location(*latLonPair)

        location = Location(*latLon)
        self.assertEqual(latLon[0], location.latitude)
        self.assertEqual(latLon[1], location.longitude)
        self.assertEqual('42.3776, -72.5032', location.latLonTruncated())


    def testZipCodeLocation(self):
        latLonZipName = ['42.377651', '-72.50323', '01002', 'Amherst, MA']
        location = ZipCodeLocation(latLonZipName[2])
        self.assertEqual(latLonZipName[0], location.latitude)
        self.assertEqual(latLonZipName[1], location.longitude)
        self.assertEqual(latLonZipName[2], location.zipcode)
        self.assertEqual(latLonZipName[3], location.name)


    def testZipCodeUtil(self):
        query = 'barro'
        expZipNameLatLonTuples = [('54812', 'Barron, WI', '45.39701', '-91.86337'),
                                  ('54813', 'Barronett, WI', '45.646145', '-92.01923'),
                                  ('99723', 'Barrow, AK', '71.299525', '-156.74891')]
        zipNameLatLonTuples = searchZipcodes(query)
        self.assertListEqual(expZipNameLatLonTuples, zipNameLatLonTuples)

        for expZipNameLatLon in expZipNameLatLonTuples:
            latitude, longitude, name = latLonNameForZipcode(expZipNameLatLon[0])
            self.assertEqual(expZipNameLatLon[2], latitude)
            self.assertEqual(expZipNameLatLon[3], longitude)
            self.assertEqual(expZipNameLatLon[1], name)

        with self.assertRaisesRegex(ValueError, "couldn't find zipcode: 99999"):
            latLonNameForZipcode('99999')

