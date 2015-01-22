# Introduction
This is a simple proof-of-concept web app to display outside weather conditions in an 'at a glance' format where each
hour is a cell that is 'stoplight' color coded based on how good it appears for activities like RC flying.

Obviously the two big factors in how useful this app is are 1) quality of underlying weather data, and 2) quality of
the hourly analysis-to-color algorithm.


# Bugs
- time display doesn't localize to zip code :-) ex: at 2015-01-22 10.47a: https://rc-weather.herokuapp.com/forecast/77001
  says: "Forecast for Houston, TX - 77001 at Thu, 01/22, 03:47 PM". It's currently using whatever 'now' means on the
  heroku server
- https://rc-weather.herokuapp.com/forecast/09003 -> Internal Server Error
- images stretch based on window size :-O


# Feature Requests: Active
## Essential
- modern appearance
    - mobile-friendly (responsive design)
    
- daylight: factor in
    - transparent, or somehow make "less visible" the hours when it's dark
    - show the sunset and sunrise times. smarter daylight calculation (don't show if dusk or night). Perhaps grey-out, make

- more parameters?
    - DEC: Apparent Temperature, Wind Speed, PoP12, Sky Cover. maybe for click: Weather Conditions Icons. This would be
      FOUR parameters, each with three desirability ratings.
        - Currently we have THREE parameters, three ratings each, and FOUR hourly ratings:
          CURRENT RULES: L**, MMH, MHH, HHH
        - If we have FOUR params then we have these FIVE combinations:
          NEW RULES : L***, MMMH, MMHH, MHHH, HHHH
        - But is five colors getting out of hand? Which one inner pattern would we toss to keep four? The choice would be
          arbitrary. However, maybe we could indicate sky cover separately, say by HSV or pattern? Nah - too complicated.
          DEC: expand to FIVE hourly ratings and colors.

- select your own parameters as to what constitutes a "green block" (No login is required - can store in a cookie)
    - every user should be able to specify what is acceptable in terms of: 1. Wind, 2. Rain (or snow), 3. Temperature
    - edit the "acceptable" values via sliders and then to set priorities by weight
    - simple sliders to adjust thresholds for temp, clouds, and wind preferences

- chosing location
    - add APO zipcodes - http://www.us-zip.org/armed_forces/apo/
    - input GPS coordinates as an option rather than just zip
    - allow city, state. Many times when you are traveling or going out of your local area, you know the town name but
      not the zip code. Saves a step of "looking it up".


## Secondary
- click a block to show details


## Maybe or for fun
- add a link to this page, say on github? Q: do I want to make the source open?
- overall assessment
    - Use a picture/icon :-)
- rethink layout/squares?
    - have long term squares, with users able to set their thresholds for bad, acceptable and great flying days, and
      then have a short term meteogram for double checking nearer the time.
    - show every three hours instead of one? After all, that's the most frequent update of data
- show a sunny/overcast/rain/snow icon in the hour square like http://www.alessioatzeni.com/meteocons/res/img/screen.png
- international
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


## Tagline: "Just look for the green and then go fly!"
