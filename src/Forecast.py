import csv


class Forecast:
    def __init__(self, zipcode):
        self.zipcode = zipcode


    # TODO preload file into memory
    @staticmethod
    def lat_long_name_for_zipcode(zipcode):
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
        raise ValueError("invalid zipcode {}".format(zipcode))
