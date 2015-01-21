# Introduction
This is a simple proof-of-concept web app to display outside weather conditions in an 'at a glance' format where each
hour is a cell that is 'stoplight' color coded based on how good it appears for activities like RC flying.

Obviouly the two big factors in how useful this app is are 1) quality of underlying weather data, and 2) quality of
the hourly analysis-to-color algorithm.


# To Do
- BIG: professional design and style :-)

- BIG: weather data quality. Q: why doesn't my data match that of the gov's?
  http://forecast.weather.gov/MapClick.php?w0=t&w2=wc&w3=sfcwind&w3u=1&w4=sky&w5=pop&w8=rain&w9=snow&AheadHour=0&Submit=Submit&FcstType=graphical&textField1=42.37510&textField2=-72.52000&site=all&unit=0&dd=0&bw=0

- BIG: improve hourly analysis algorithm

- overall summary
- do smarter daylight calculation? (don't show if dusk or night)


# Suggestions and comments from forum postings on 2015-01-19
http://helifreak.com/showthread.php?p=6307025#post6307025
http://rc.runryder.com/helicopter/t781886p1/?p=6427847#RR

- 4 factor in daylight. show the sunset and sunrise times. Perhaps grey-out, make transparent, or somehow make
  "less visible" the hours when it's dark
- 3 select your own parameters as to what constitutes a "green block"
  - every user should be able to specify what is acceptable in terms of: 1. Wind, 2. Rain (or snow), 3. Temperature
  - edit the "acceptable" values via sliders and then to set priorities by weight
  - simple sliders to adjust thresholds for temp, clouds, and wind preferences
- 2 factor in overcast. Please consider whether the day is sunny or cloudy. Makes a huge difference in experience
  (at least here in OR).
- 3 mobile app. embedded as a widget on my phone

- allow city, state. Many times when you are traveling or going out of your local area, you know the town name but not
  the zip code. Saves a step of "looking it up".
- colors:  3. It's slightly confusing whether orange or yellow is better. Not sure how to address this. Maybe add a
  little green to that yellow, and a little more red to that orange?
- Show a sunny/overcast/rain/snow icon in the hour square like http://www.alessioatzeni.com/meteocons/res/img/screen.png
- temperature: Base the temperature rating on the normal temps for the area of the country. In theory, a person would
  be aclimated to the normal temperature trend. For example, in Texas in summer, the temp rating component as you
  currently have it defined would almost always be low. Better yet, base it on heat index. 90 degrees in Houston is a
  lot less comfortable than 90 degrees in Dallas.
- input GPS coordinates as an option rather than just zip
- add in APO zipcodes
- outside US
- alerts: mobile app that alerts me when local conditions are "green"
- integrate it with the existing android/iOS calendars (shade the background of your calendar's hourly blocks with the
  flying condition colors). could see my actual appointments etc while being able to see flying conditions at a glance
  (and schedule everything for red times!)


## Technical
- Responsive web site design
- No login is required since this can be stored in a cookie

## Referenced apps/sites
- ! [ETSU Observatory Clear Sky Chart](http://cleardarksky.com/c/ETSUObTNkey.html?1)
- [WindAlert iOS App] (https://itunes.apple.com/us/app/windalert/id317992025?mt=8)
- [Windalert](http://www.windalert.com/)
- [Meteogram weather widget](https://play.google.com/store/apps/details?id=be.inet.rainwidget)
   yellow for wind, blue bars for rainfall, and colour coded temperature


## Tagline: "just look for the "green" and then fly"
