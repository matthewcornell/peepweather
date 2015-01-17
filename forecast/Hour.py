from functools import total_ordering


class Rating:
    # pseudo enum per http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    Poor, Marginal, Great = range(0, 3)


@total_ordering
class Hour():

    def __init__(self, datetime, precip=None, temp=None, wind=None):
        """
        pass None for the weather variables to represent missing data, i.e., a 'missing' hour
        :param datetime: 
        :param precip: 
        :param temp: 
        :param wind: 
        :return:
        """
        self.datetime = datetime    # time of forecast. always on the hour, i.e., only the day and hour matter. minutes, etc. are ignored
        self.precip = precip        # probability of precipitation: % b/w 0 and 100
        self.temp = temp            # degrees Fahrenheit
        self.wind = wind            # MPH


    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, repr(self.datetime),
                                           self.precip, self.temp, self.wind)


    def key(self):
        return self.datetime, self.precip, self.temp, self.wind


    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()


    def __hash__(self):
        return hash(self.key())
    
    
    def __lt__(self, other):
        return self.datetime < other.datetime


    #
    # TODO temporary, untested
    # TODO instead of a color, return a Rating enum value, and let the css map to colors
    # Awesome!: https://en.wikipedia.org/wiki/Miscellaneous_Symbols , e.g., U+2600 / &#9728; for 'Black sun with rays'
    #
    # Q: where does &blacksquare; come from? aha:
    # https://code.google.com/p/doctype-mirror/source/browse/BlacksquareCharacterEntity.wiki?repo=wiki&r=043f3193936e69f951d7fe19f78a0cbdd2ed526b&spec=svn.wiki.c717498c6a9e256495b8d098dc575f787acc0b7d
    # https://code.google.com/p/doctype-mirror/wiki/CharacterEntities
    # https://html.spec.whatwg.org/multipage/syntax.html#named-character-references , 
    # http://www.w3.org/TR/html4/sgml/entities.html
    #
    def color(self):
        """
        :return: an html color string based on my weather settings.
            3-tuple of HTML color name strings for precip, temp, and wind based on temporary rules in this method
        """
        # missing hour special case
        if not self.precip:
            return 'white'

        # rate each variable separately, then combine
        if self.precip < 20:
            precipRating = Rating.Great
        elif self.precip > 40:
            precipRating = Rating.Poor
        else:
            precipRating = Rating.Marginal

        if self.temp < 30 or self.temp > 80:
            tempRating = Rating.Poor
        elif 55 < self.temp < 75:
            tempRating = Rating.Great
        else:
            tempRating = Rating.Marginal

        if self.wind < 5:
            windRating = Rating.Great
        elif self.wind > 10:
            windRating = Rating.Poor
        else:
            windRating = Rating.Marginal

        # combine ratings to get a final color
        if precipRating == Rating.Poor or tempRating == Rating.Poor or windRating == Rating.Poor:
            color = 'red'
        elif precipRating == Rating.Marginal or tempRating == Rating.Marginal or windRating == Rating.Marginal:
            color = 'yellow'
        else:
            color = 'green'

        return color
    