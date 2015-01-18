# Introduction
This is a simple proof-of-concept web app to display outside weather conditions in an 'at a glance' format where each
hour is a cell that is 'stoplight' color coded based on how good it appears for activities like RC flying.


# The big question: Utility
There are primarily two main factors that determine this app's utility: the quality of 1) the weather data, and 2) the
analysis algorithm.

## Weather data quality
- issue: why doesn't my data match that of the gov's? http://forecast.weather.gov/MapClick.php?w0=t&w2=wc&w3=sfcwind&w3u=1&w4=sky&w5=pop&w8=rain&w9=snow&AheadHour=0&Submit=Submit&FcstType=graphical&textField1=42.37510&textField2=-72.52000&site=all&unit=0&dd=0&bw=0

## Hourly analysis algorithm
- this could use some (fun!) tweaking


# Evaluation
Basically I need some folks to take a look and tell me what they think :-)


# Issues
- don't show column if all white b/c non-white only in unshown hours (night)
- ...


# To Do
- change color key to pull values from code

## Features
- geolocation?
- forms for entering zip, and for entering query
- eventually a form to specify color ranges for parameters
- do smarter daylight calculation (don't show if dusk or night)?
- overall summary

## Appearance
- professional design and style!
- show why color chosen - tooltip? list?
- page titles include name
- about page - this readme file?
- debug link to data URL (lat, lon)
