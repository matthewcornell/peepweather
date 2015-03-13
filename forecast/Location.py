from forecast.ZipCodeUtil import latLonNameForZipcode


class Location(object):
    """
    A latitude/longitude-based location. Concrete class.
    """


    def __init__(self, latitude, longitude):
        if not latitude or not longitude:
            raise ValueError("invalid format for latitude or longitude: None")

        self.latitude = latitude
        self.longitude = longitude

        
    def __repr__(self):
        return '{cls}({latitude}, {longitude})'.format(
            cls=self.__class__.__name__, latitude=self.latitude, longitude=self.longitude)


    def latLonTruncated(self):
        # truncate to four digits after decimal
        latStr = self.latitude[:self.latitude.index('.') + 5]
        lonStr = self.longitude[:self.longitude.index('.') + 5]
        return '{}, {}'.format(latStr, lonStr)


class ZipCodeLocation(Location):
    """
    A Location with zip code information. Looked up via ZipCodeUtil (zip code file).
    """


    def __init__(self, zipcode):
        latitude, longitude, name = latLonNameForZipcode(zipcode)
        super().__init__(latitude, longitude)
        self.zipcode = zipcode
        self.name = name


    def __repr__(self):
        return '{cls}({zipcode})'.format(
            cls=self.__class__.__name__, zipcode=self.zipcode)
