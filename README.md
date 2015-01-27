# Introduction
This is a simple proof-of-concept web app to display outside weather conditions in an 'at a glance' format where each
hour is a cell that is 'stoplight' color coded based on how good it appears for activities like RC flying.

Obviously the two big factors in how useful this app is are 1) quality of underlying weather data, and 2) quality of
the hourly analysis-to-color algorithm.


# Bugs
- cookies: use secure?

- form validation:
    - /       : zipcode: not empty. five numbers. exists in zipcode file.
    - /       : lat/lon: not empty. lat/lon pattern
    - /ranges : param values: not empty. ints. sorted
    - /search : not empty


# Feature Requests: Active

## Essential
- add Sky Cover. have to re-think Hour.hourDesirabilityForParamDesCounts()

- daylight: factor in
    - transparent, or somehow make "less visible" the hours when it's dark
    - show the sunset and sunrise times. smarter daylight calculation (don't show if dusk or night). Perhaps grey-out, make

- modern appearance
    - mobile-friendly (responsive design)

- editable parameter weights for combined importance to the final rating


## Money to fund hosting?
- paypal donate
- ads


## Maybe for fun
- geolocation :-)

- palette selection. multiple css files, popup 

- click a square to show details

- palette choices - css should make it easy :-)

- overall assessment
    - Use a picture/icon :-)

- rethink layout/squares?
    - have long term squares, with users able to set their thresholds for bad, acceptable and great flying days, and
      then have a short term meteogram for double checking nearer the time.
    - show every three hours instead of one? After all, that's the most frequent update of data

- show a sunny/overcast/rain/snow icon in the hour square like http://www.alessioatzeni.com/meteocons/res/img/screen.png

- list/map AMA fields nearby :-)
  http://www.modelaircraft.org/clubsearch.aspx
  python screen scraper - http://www.crummy.com/software/BeautifulSoup/

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


# Feature Requests: Future
- colors: a gradient of each color to indicate really low wind (0-3,3-6,6-9), etc. that way we can really know a 1mph day vs 9 mph day?


# Above includes suggestions and comments from forum postings on 2015-01-19
- [Helifreak: Check out my RC Weather 'at a glance' proof-of-concept!](http://helifreak.com/showthread.php?p=6307025#post6307025)
- [RunRyder: Check out my RC Weather 'at a glance' proof-of-concept!](http://rc.runryder.com/helicopter/t781886p1/?p=6427847#RR)


## Technical
- No login is required since this can be stored in a cookie


## Site design ideas
- [Windalert](http://www.windalert.com/)


## Referenced apps/sites
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


## Tagline: "Just look for the green and then go fly!"
