import csv


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


    @classmethod
    def hoursForDwmlXmlRoot(cls, dwmlElement):
        """
        :param dwmlElement:
        :return: a sequence of Hour instances corresponding to the passed DWML document element
        """
        hours = []
        
        # TODO
        
        return hours
