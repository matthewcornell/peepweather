from PIL import Image, ImageDraw


class Sticker:
    """
    """

    def __init__(self, forecast):
        """
        :return: an instance whose image property is a PIL Image corresponding to forecast to be used for sticker embedding

        todo:
        o make header prettier - say with a gray background, existing brand image, etc.
        o use nicer font, such as TrueType. NB: default is courB08 in ImageFont.py. others were too big: via http://www.geeks3d.com/20131108/beginning-with-pillow-the-pil-fork-python-imaging-library-tutorial-programming/7/
        o Q: del(draw)?

        """
        self.forecast = forecast
        self.tableSize = (126, 187)  # excluding brand but including row and column headers
        self.brandSize = (self.tableSize[0], 12)
        self.imageSize = self.tableSize[0], self.tableSize[1] + self.brandSize[1]
        self.image = Image.new('RGB', self.imageSize, 'white')
        self.drawLocation()
        self.drawBrand()
        self.drawSquaresRowColHeadsGrid()


    def drawColumnHeadings(self, squareSize):
        for idx, colHeader in enumerate(self.forecast.calendarHeaderRow()):
            x, y = squareSize[0] + (squareSize[0] * idx), self.brandSize[1]
            draw = ImageDraw.Draw(self.image)
            draw.text((x + 2, y), colHeader, 'black')


    def drawSquaresRowColHeadsGrid(self):
        # for now all squares, including row and column headers, are equal sizes
        firstHour, numHours = 8, 13  # 8a to 8p
        hoursAsCalendarRows = self.forecast.hoursAsCalendarRows()
        numCols = len(hoursAsCalendarRows[0]) + 1  # including row header
        # excluding brand and column header
        squareSize = self.tableSize[0] / numCols, (self.tableSize[1] - self.brandSize[1]) / (
        numHours + 1)  # including column header
        self.drawColumnHeadings(squareSize)
        for rowNum in range(numHours):  # hour of day rows. excludes column header
            # x, y = upper left corner. y skips brand height and column header row
            x, y = 0, self.brandSize[1] + squareSize[1] + (squareSize[1] * rowNum)
            hourOfDayIndex = rowNum + firstHour
            hourOfDayRow = hoursAsCalendarRows[hourOfDayIndex]
            rowHeadingColor = 'black' if hourOfDayRow[0].isDaylight(
                self.forecast) else 'gray'  # todo cleaner if css classes
            rowHeading = self.forecast.rowHeadingForHour(hourOfDayIndex)  # '8', '12p', etc.
            self.drawRowHeading(x, y, rowHeading, rowHeadingColor)
            for hour in hourOfDayRow:  # day of week columns
                x += squareSize[0]
                self.drawHourSquare(x, y, squareSize, hour)
        self.drawGrid(squareSize, numCols, numHours)


    def drawRowHeading(self, x, y, rowHeading, rowHeadingColor):
        draw = ImageDraw.Draw(self.image)
        draw.text((x + 2, y), rowHeading, rowHeadingColor)


    def drawHourSquare(self, x, y, squareSize, hour):
        cssClass = hour.cssClassForDesirability(self.forecast.rangeDict)
        cssClassToColor = {
            'Poor': '#ff0000',
            'Fair': '#ffaa00',
            'Okay': '#d5ff00',
            'Great': '#00ff00',
            'Missing': 'white',  # ffffff
        }  # todo should probably grab this from hour-colors.css in case it changes
        hourColor = cssClassToColor[cssClass]
        draw = ImageDraw.Draw(self.image)
        draw.rectangle((x, y, x + squareSize[0], y + squareSize[1]), hourColor)


    def drawGrid(self, squareSize, numCols, numRows):
        draw = ImageDraw.Draw(self.image)
        # draw horiz lines. include extra above column headers
        lineColor = 'gray'
        for rowNum in range(numRows + 2):
            x1, y1 = 0, self.brandSize[1] + (squareSize[1] * rowNum)
            x2 = self.tableSize[0]
            draw.line([x1, y1, x2, y1], lineColor)
        # draw vertical lines. include extra left of row headers
        for colNum in range(numCols + 1):
            x1, y1 = squareSize[0] * colNum, self.brandSize[1]
            y2 = self.tableSize[1]
            if colNum == numCols:
                x1 -= 1  # a hack to keep the rightmost line from being clipped
            draw.line([x1, y1, x1, y2], lineColor)


    def drawLocation(self):
        location = self.forecast.location
        x, y = 10 if location.zipcode else 13, -1  # hack to center. s/b based on font
        zipOrLatLon = location.zipcode if location.zipcode else location.latLonTruncated()
        location = ("Forecast for " if location.zipcode else "") + zipOrLatLon
        draw = ImageDraw.Draw(self.image)
        draw.text((x, y), location, 'gray')


    def drawBrand(self):
        x, y = 0, self.tableSize[1] + 1
        brandText = "PeepWeather.com"
        draw = ImageDraw.Draw(self.image)
        draw.text((x + 18, y - 1), brandText, 'gray')  # offsets are magic - should be based on font
