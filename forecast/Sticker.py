from PIL import Image


class Sticker:
    def __init__(self, forecast):
        """
        :return: an instance whose image property is a PIL Image corresponding to forecast to be used for sticker embedding
        """
        self.forecast = forecast
        self.tableSize = (126, 187)
        self.brandSize = (self.tableSize[0], 20)
        self.imageSize = self.tableSize[0] + self.brandSize[0], self.tableSize[1] + self.brandSize[1]
        self.image = Image.new('RGB', self.imageSize)
        self.drawRowHeadings()
        self.drawColumnHeadings()
        self.drawSquares()
        self.drawGrid()
        self.drawBrand()

        # todo for now a temporary png file so we have an Image to work with:
        self.image = Image.open('/Users/matt/IdeaProjects/rc-weather-flask/app/static/sticker-126x187-temp.png')


    def drawRowHeadings(self):
        pass


    def drawColumnHeadings(self):
        pass


    def drawSquares(self):
        # for now all squares, including row and column headers, are equal sizes
        firstHour, numHours = 8, 13  # 8a to 8p
        hoursAsCalendarRows = self.forecast.hoursAsCalendarRows()
        numCols = len(hoursAsCalendarRows[0])
        squareSize = self.tableSize[0] / numCols, self.tableSize[1] / numHours  # AKA numRows
        print('xx')
        for hourNum in range(numHours):
            hourOfDayIndex = hourNum + firstHour
            x, y = squareSize[0] * 1, self.brandSize[1] + squareSize[1] * 1  # upper left corner, x skipping row header column, y skipping brand height and column header row
            hourOfDayRow = hoursAsCalendarRows[hourOfDayIndex]
            rowHeadingColor = 'black' if self.forecast.isDaylightHour(hourOfDayRow[0]) else 'gray'  # todo cleaner if css classes
            rowHeading = self.forecast.rowHeadingForHour(hourOfDayIndex)  # '8', '12p', etc.
            print('  idx={}, rhc={}, rh={}'.format(hourOfDayIndex, rowHeadingColor, rowHeading))
            self.drawRowHeading(x, y, squareSize, rowHeading, rowHeadingColor)
            for hour in hourOfDayRow:
                cssClass = hour.cssClassForDesirability()
                print('    css={}, hc={} -- hr={}'.format(cssClass, cssClass, hour))
                self.drawHour(x, y, squareSize, cssClass)


    def drawGrid(self):
        pass


    def drawBrand(self):
        pass


    def drawRowHeading(self, x, y, squareSize, rowHeading, rowHeadingColor):
        pass


    def drawHour(self, x, y, squareSize, cssClass):
        cssClassToColor = {
            'Poor': '#ff0000',
            'Fair': '#ffaa00',
            'Okay': '#d5ff00',
            'Great': '#00ff00',
            'Missing': 'white',  # ffffff
        }  # todo should probably grab this from hour-colors.css in case it changes
        hourColor = cssClassToColor[cssClass]
        pass
