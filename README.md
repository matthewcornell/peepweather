# Introduction
This is a simple proof-of-concept web app to display outside weather conditions in an 'at a glance' format where each
hour is a cell that is 'stoplight' color coded based on how good it appears for activities like RC flying.

Obviously the two big factors in how useful this app is are 1) quality of underlying weather data, and 2) quality of
the hourly analysis-to-color algorithm.


# current branch todo
- ! table columns not fixed width in chrome and safari
- see: todo integrate with bootstrap
- zip/latlon input: remove spaces around comma
- share icons
- when done: geo!
- xx


# Bugs
- ! form validation:
    - /       : zipcode: not empty. five numbers. exists in zipcode file.
    - /       : lat/lon: not empty. lat/lon pattern
    - /ranges : param values: not empty. ints. sorted
    - /search : not empty

- ? sunrise/set off by an hour? current: twilight = -12 * ephem.degree
  http://stackoverflow.com/questions/26501745/how-to-determine-if-it-is-daytime-light-outside-in-python-using-ephem-library
  http://rhodesmill.org/pyephem/rise-set.html#computing-twilight
  http://stackoverflow.com/questions/2637293/calculating-dawn-and-sunset-times-using-pyephem
  fred.horizon = '-6' #-6=civil twilight, -12=nautical, -18=astronomical

- ? cookies: use secure?


# Feature requests: Essential
- geolocation :-)

- ~ a checkbox controlling whether apparent or actual temp is used

- ~ daylight: add new setting for defining which hours to show - start, end (inclusive), rather than hard-coded


# Money to fund hosting?
- paypal donate
- ads


# Feature requests: Maybe for fun
- recently found on right - last 5 or so :-)

- list/map AMA fields nearby :-)
  http://www.modelaircraft.org/clubsearch.aspx
  python screen scraper - http://www.crummy.com/software/BeautifulSoup/

- ~ click a square to show details

- ~ editable parameter weights for combined importance to the final rating

- international. I don't know the details myself, but drop Benny Wydooghe a line on google+, or in the Meteogram Widget
  group on google+. He's the developer of the widget I posted a screenshot of earlier, and has a great international
  weather service he uses. He's had to work through all these timezone issues, provider issues, etc himself so he'd
  probably be a good contact for you. - http://helifreak.com/showpost.php?p=6317185&postcount=89

- mobile app
    - widget
    - alerts: mobile app that alerts me when local conditions are "green"
    - the integrate it with the existing android/iOS calendars (shade the background of your calendar's hourly blocks
      with flying condition colors). could see my actual appointments etc while being able to see flying conditions at
      a glance (and schedule everything for red times!)


# Above includes suggestions and comments from forum postings on 2015-01-19
- [Helifreak: Check out my RC Weather 'at a glance' proof-of-concept!](http://helifreak.com/showthread.php?p=6307025#post6307025)
- [RunRyder: Check out my RC Weather 'at a glance' proof-of-concept!](http://rc.runryder.com/helicopter/t781886p1/?p=6427847#RR)


# Referenced apps/sites
- [Windalert](http://www.windalert.com/)
- ! [ETSU Observatory Clear Sky Chart](http://cleardarksky.com/c/ETSUObTNkey.html?1)
- [WindAlert iOS App] (https://itunes.apple.com/us/app/windalert/id317992025?mt=8)
- [Windalert](http://www.windalert.com/)
- [Meteogram weather widget](https://play.google.com/store/apps/details?id=be.inet.rainwidget)
   yellow for wind, blue bars for rainfall, and colour coded temperature
- [Windyty, wind forecast](https://www.windyty.com/spot/location/42.374/-72.518/name/Amherst?surface,wind,now,42.374,-72.264,11)
- [Aviation Weather Report and Forecast - Wind Speed, Temperature, Wind Direction, Precipitation Forecast](http://www.usairnet.com/cgi-bin/launch/code.cgi?state=TX&sta=KTKI)
- [meteocons](http://www.alessioatzeni.com/meteocons/res/img/screen.png)
- [1Weather:Widget Forecast Radar | 1mobile.com] (http://www.1mobile.com/1weather-widget-forecast-radar-336436.html)
- [windalert.com] (http://windalert.com/map#42.375,-72.513,10,1)


# Tagline: "Just look for the green and then go fly!"
