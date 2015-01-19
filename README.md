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
