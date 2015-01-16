import csv

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

CACHED_ZIP_INFO_TUPLES = makeZipInfoTuples()
