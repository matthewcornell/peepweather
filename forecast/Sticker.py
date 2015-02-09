from PIL import Image


class Sticker:
    def __init__(self, forecast):
        """
        :return: an instance whose image property is a PIL Image corresponding to forecast to be used for sticker embedding
        """
        self.forecast = forecast
        self.tableSize = (126, 187)
        self.brandSize = (self.tableSize[0], 20)
        self.image = Image.new('RGB', (self.tableSize[0] + self.brandSize[0], self.tableSize[1] + self.brandSize[1]))
        self.drawSquares()
        self.drawColumnHeadings()
        self.drawGrid()
        self.drawBrand()

        # todo for now a temporary png file so we have an Image to work with:
        self.image = Image.open('/Users/matt/IdeaProjects/rc-weather-flask/app/static/sticker-126x187-temp.png')


    def drawSquares(self):
        cssClassToColor = {
            'Poor': '#ff0000',
            'Fair': '#ffaa00',
            'Okay': '#d5ff00',
            'Great': '#00ff00',
            'Missing': 'white',  # ffffff
        }  # todo should probably grab this from hour-colors.css in case it changes
        hoursAsCalendarRows = self.forecast.hoursAsCalendarRows()
        print('xx')
        for hourOfDayIndex in range(8, 21):
            hourOfDayRow = hoursAsCalendarRows[hourOfDayIndex]
            hour0 = hourOfDayRow[0]
            rowHeadingColor = 'black' if self.forecast.isDaylightHour(hour0) else 'gray'  # todo cleaner if css classes
            rowHeading = self.forecast.rowHeadingForHour(hourOfDayIndex)  # 8, 9, ..., 12p, 1p, ... 8p
            print('  idx={}, rhc={}, rh={}'.format(hourOfDayIndex, rowHeadingColor, rowHeading))
            for hour in hourOfDayRow:
                cssClass = hour.cssClassForDesirability()
                hourColor = cssClassToColor[cssClass]
                print('    hr={}. css={}, hc={}'.format(hour, cssClass, hourColor))
                # todo!


    def drawColumnHeadings(self):
        headerRow = self.forecast.calendarHeaderRow()
        # todo!


    def drawGrid(self):
        pass  # todo!


    def drawBrand(self):
        pass  # todo!
