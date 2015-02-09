from PIL import Image, ImageDraw, ImageFont


class Sticker:
    def __init__(self, forecast):
        """
        :return: an instance whose image property is a PIL Image corresponding to forecast to be used for sticker embedding
        todo think: del(draw)
        """
        self.forecast = forecast
        self.tableSize = (126, 187)     # excluding brand but including row and column headers
        self.brandSize = (self.tableSize[0], 20)
        self.imageSize = self.tableSize[0] + self.brandSize[0], self.tableSize[1] + self.brandSize[1]
        self.image = Image.new('RGB', self.imageSize, 'white')
        self.drawSquaresRowColHeadsGrid()
        self.drawBrand()
        self.drawOverallOutline()

        # todo for now a temporary png file so we have an Image to work with:
        # self.image = Image.open('/Users/matt/IdeaProjects/rc-weather-flask/app/static/sticker-126x187-temp.png')


    def drawColumnHeadings(self,squareSize):
        print('drawColumnHeadings()')
        for idx, colHeader in enumerate(self.forecast.calendarHeaderRow()):
            x, y = squareSize[0] + (squareSize[0] * idx), self.brandSize[1]
            print('  drawColumnHeadings(): x,y={},{}. h={}'.format(x, y, colHeader))
            draw = ImageDraw.Draw(self.image)
            draw.text((x, y), colHeader, 'black')


    def drawSquaresRowColHeadsGrid(self):
        # for now all squares, including row and column headers, are equal sizes
        firstHour, numHours = 8, 13  # 8a to 8p
        hoursAsCalendarRows = self.forecast.hoursAsCalendarRows()
        numCols = len(hoursAsCalendarRows[0]) + 1   # including row header
        # excluding brand and column header
        squareSize = self.tableSize[0] / numCols, (self.tableSize[1] - self.brandSize[1]) / (numHours + 1)    # including column header
        print('drawSquaresRowColHeadsGrid(): ts={}, bs={} | nc={}, nr={}, ss={}'.format(self.tableSize, self.brandSize, numCols, range(numHours), squareSize))
        self.drawColumnHeadings(squareSize)
        for rowNum in range(numHours):  # hour of day rows. excludes column header
            # x, y = upper left corner. y skips brand height and column header row
            x, y = 0, self.brandSize[1] + squareSize[1] + (squareSize[1] * rowNum)
            hourOfDayIndex = rowNum + firstHour
            hourOfDayRow = hoursAsCalendarRows[hourOfDayIndex]
            rowHeadingColor = 'black' if self.forecast.isDaylightHour(hourOfDayRow[0]) else 'gray'  # todo cleaner if css classes
            rowHeading = self.forecast.rowHeadingForHour(hourOfDayIndex)  # '8', '12p', etc.
            self.drawRowHeading(x, y, rowHeading, rowHeadingColor)
            for hour in hourOfDayRow:  # day of week columns
                x += squareSize[0]
                cssClass = hour.cssClassForDesirability()
                self.drawHourSquare(x, y, squareSize, cssClass)
        self.drawGrid(squareSize, numCols, numHours)


    def drawRowHeading(self, x, y, rowHeading, rowHeadingColor):
        print('  drawRowHeading(): x,y={},{}. rh,rhc={},{}'.format(x, y, rowHeading, rowHeadingColor))
        draw = ImageDraw.Draw(self.image)
        draw.text((x, y), rowHeading, rowHeadingColor)


    def drawHourSquare(self, x, y, squareSize, cssClass):
        cssClassToColor = {
            'Poor': '#ff0000',
            'Fair': '#ffaa00',
            'Okay': '#d5ff00',
            'Great': '#00ff00',
            'Missing': 'white',  # ffffff
        }  # todo should probably grab this from hour-colors.css in case it changes
        hourColor = cssClassToColor[cssClass]
        print('    drawHourSquare(): x,y={},{}. hc={}'.format(x, y, hourColor))
        draw = ImageDraw.Draw(self.image)
        draw.rectangle((x, y, x + squareSize[0], y + squareSize[1]), hourColor)


    def drawGrid(self, squareSize, numCols, numRows):
        print('drawGrid(): nc,nr={},{}'.format(numCols, numRows))
        draw = ImageDraw.Draw(self.image)
        # draw horiz lines. include extra above column headers
        lineColor = 'gray'
        for rowNum in range(numRows + 1):
            x1, y1 = 0, self.brandSize[1] + (squareSize[1] * rowNum)
            x2 = self.tableSize[0]
            print('  drawGrid() horiz: rn={}, x1,y1={},{}. x2={}'.format(rowNum, x1, y1, x2))
            draw.line([x1, y1, x2, y1], lineColor)
        # draw vertical lines. include extra left of row headers
        for colNum in range(numCols + 1):
            x1, y1 = squareSize[0] * colNum, self.brandSize[1]
            y2 = self.tableSize[1]
            print('  drawGrid() vert: cn={}, x1,y1={},{}. y2={}'.format(colNum, x1, y1, y2))
            draw.line([x1, y1, x1, y2], lineColor)


    def drawBrand(self):
        # todo Q: use existing brand image?
        x, y = 0, 0
        brandText = "PeepWeather.com"
        print('drawBrand(): x,y={},{}. h={}'.format(x, y, brandText))
        # self.brandSize[1]
        draw = ImageDraw.Draw(self.image)
        draw.text((x, y), brandText, 'black')


    def drawOverallOutline(self):
        # light gray around entire table
        pass
    
