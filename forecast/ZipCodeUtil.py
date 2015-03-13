import csv

import re


def makeZipInfoTuples():
    """
    Loads zipcode-clean.csv into memory
    :return: a list of 5-tuples of the form: (csv_zipcode, city, state, latitude, longitude)
    """
    zipInfoTuples = []
    with open('forecast/zipcode-clean.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for (csv_zipcode, city, state, latitude, longitude, timezone, dst) in csvreader:
            zipInfoTuples.append((csv_zipcode, city, state, latitude, longitude))
    return zipInfoTuples


def latLonNameForZipcode(zipcode):
    """
    :param zipcode:
    :return: looks up and returns information for zipcode as a 3-tuple of the form: (latitude, longitude, name)
    """
    for (csv_zipcode, city, state, latitude, longitude) in CACHED_ZIP_INFO_TUPLES:
        if csv_zipcode == zipcode:
            return latitude, longitude, city + ", " + state
    raise ValueError("couldn't find zipcode: {}".format(zipcode))


def searchZipcodes(query):
    """
    :param query: 
    :return: a list of 4-tuples containing places matching query. format: (zipcode, name, latitude, longitude),
    where name is the same as latLonNameForZipcode()
    """
    zipNameTuples = []
    for (csv_zipcode, city, state, latitude, longitude) in CACHED_ZIP_INFO_TUPLES:
        name = city + ", " + state
        if re.search(query, name, re.IGNORECASE):
            zipNameTuples.append((csv_zipcode, name, latitude, longitude))
    return sorted(zipNameTuples, key=lambda theTuple: theTuple[1])


CACHED_ZIP_INFO_TUPLES = makeZipInfoTuples()

