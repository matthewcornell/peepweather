from forecast.ZipCodeUtil import latLonNameForZipcode


class Location(object):
    """
    A latitude/longitude-based location with optional zip code and name information.
    """


    def __init__(self, zipOrLatLon):
        """
        :param zipOrLatLon: location to get the forecast for. either a zip code string or a 2-tuple of latitude and
        longitude strings. ex: '01002' or ('42.375370', '-72.519249').
        """
        if type(zipOrLatLon) == str:
            (lat, lon, name) = latLonNameForZipcode(zipOrLatLon)
            self.zipcode = zipOrLatLon
            self.latitude = lat
            self.longitude = lon
            self.name = name
        elif (type(zipOrLatLon) == list or type(zipOrLatLon) == tuple) and len(zipOrLatLon) == 2 \
                and type(zipOrLatLon[0]) == str \
                and type(zipOrLatLon[1]) == str:
            self.zipcode = None
            self.latitude = zipOrLatLon[0]
            self.longitude = zipOrLatLon[1]
            self.name = None
        else:
            raise ValueError("location wasn't a zip code or comma-separated lat/lon: {}".format(zipOrLatLon))


    def __repr__(self):
        zipOrLatLon = self.zipcode if self.zipcode else (self.latitude, self.longitude)
        return '{cls}({zipOrLatLon!r})'.format(cls=self.__class__.__name__, zipOrLatLon=zipOrLatLon)


    def latLonTruncated(self):
        # truncate to four digits after decimal
        latStr = self.latitude[:self.latitude.index('.') + 5]
        lonStr = self.longitude[:self.longitude.index('.') + 5]
        return '{}, {}'.format(latStr, lonStr)
