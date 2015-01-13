import unittest

from Forecast import Forecast


# TODO: more!
class MyTestCase(unittest.TestCase):
    
    # def test_make_forecast(self):
    # forecast = Forecast("01002")
    # self.assertEqual("01002", forecast.zipcode)

    def test_lookup_zip_info(self):
        exp_lat_lon_name = {"01002": ("42.377651", "-72.50323", "Amherst, MA"),
                            "92105": ("32.741256", "-117.0951", "San Diego, CA")}
        for zipcode, exp_lat_lon_name in exp_lat_lon_name.items():
            act_lat_lon_name = Forecast.lat_long_name_for_zipcode(zipcode)
            self.assertEqual(exp_lat_lon_name, act_lat_lon_name)
            
        with self.assertRaisesRegex(ValueError, 'invalid zipcode None'):
            Forecast.lat_long_name_for_zipcode(None)
