;; -*- mode: outline -*-

* bugs
** 1e /settings should validate inputs, such as 8 < 1!
** 2d text input error-checking (and forgiveness, validation)
http://flask.pocoo.org/docs/0.10/patterns/flashing/

o zip/latlon:
  o validation: not empty. zip or lat/lon pattern (zip: five numbers, exists in zipcode file)
  o trip spaces around comma, ends
  o bug: empty -> Not Found

o search:
  o not empty, matches zipcode file. ideally: completion
    http://stackoverflow.com/questions/9232748/twitter-bootstrap-typeahead-ajax-example
  o trim space from ends
  o bug: empty -> Not Found

o ranges : param values: not empty. ints. sorted

** 3d sunrise/set off by an hour? current: twilight = -12 * ephem.degree
http://stackoverflow.com/questions/26501745/how-to-determine-if-it-is-daytime-light-outside-in-python-using-ephem-library
http://rhodesmill.org/pyephem/rise-set.html#computing-twilight
http://stackoverflow.com/questions/2637293/calculating-dawn-and-sunset-times-using-pyephem
fred.horizon = '-6' #-6=civil twilight, -12=nautical, -18=astronomical

** 3d appearance: responsive: when key goes below table, it stretches full width

* features: to do
** 1e overview/summary
"Looks like the best times are __, __, and __."
"The best days to get out look to be ..."


** !1d stickers! :-)
http://www.wunderground.com/stickers/?query=Amherst,%20Massachusetts
http://www.wunderground.com/stickers/classic.html?query=Amherst,%20Massachusetts

these are awesome. ideas:
o thumbnail image of the forecast
o later: query parameters to customize (size, format, include summary, etc.)
o summary for the coming day/week - "Looks like the best times are __, __, and __."


** 1m change terminology - confusion over Low/Med/High: desirability vs. amount
o low rain vs. low desirability - high rain
o Low means Low Desirability (like Orange or Red) not low amounts of clouds

-> It might help to change the terms from Low, Medium, High to something like Bad, OK, and Great (or anything else that is more easily understandable without explanation).

** 2m use jQuery everywhere

** 3e settings: if ranges need additional clarification (or people want to learn) then have help text under each group
(wind, precip, etc.) that updates to show a sentence incorporating the current values

ex: Wind (8, 12): "Wind between 0 and 8 MPH is considered High desirability, between 8 and 12 is Medium, and anything higher than 12 is Low desirability."

* promotion ideas, branding
** use 'PeepCast' ? :-)

** think: what other integration opportunities are there?
see [embed feature for clubs' sites]

calendar integration - google or ical? see [mobile app]

helifreak and other boards (hunting, etc): a widget/link in their signature based on their profile location. maybe it shows a shrunken snapshot of the current weather? would reload every time...

** appearance: animation where chick peeks over/around something (heli, etc.) :-)

** continue: subdomains, ads, etc.

** when good enough -> announce
rc sites, clubs, etc.


* features: to consider
** appearance: don't show first column if all white?

** user accounts so that settings follow user around on every computer

** ~ favorite flying locations (like bookmarks)
add my favorite locations to a list, and have that list saved for when I come back to the home page


It could be as simple as a dropdown list somewhere. For example, a small drop down list in the header next to settings or something. It doesn't even need to have a title; an icon that represents favorites would be fine. You could then show a text hint when hovered over, or simply have it be at the top of the pop-up before your list of favorites.

I'd personally rather have one bookmark to get to all the places I care about instead of one for each location. (OK, I've only got two so far, but, hey, that could always change... )

** ~ recently found - last 5 or so :-)

** ~ daylight: add new setting for defining which hours to show - start, end (inclusive), rather than hard-coded

** ~ a checkbox controlling whether apparent or actual temp is used

** ~ editable parameter weights for combined importance to the final rating

* future: major features
** international. I don't know the details myself, but drop Benny Wydooghe a line on google+, or in the Meteogram Widget
group on google+. He's the developer of the widget I posted a screenshot of earlier, and has a great international weather service he uses. He's had to work through all these timezone issues, provider issues, etc himself so he'd  probably be a good contact for you. - http://helifreak.com/showpost.php?p=6317185&postcount=89

** mobile app
o widget
o alerts: mobile app that alerts me when local conditions are "green"
o the integrate it with the existing android/iOS calendars (shade the background of your calendar's hourly blocks with flying condition colors). could see my actual appointments etc while being able to see flying conditions at a glance (and schedule everything for red times!)


* 2015-01-19: forum postings
Helifreak: Check out my RC Weather 'at a glance' proof-of-concept!
http://helifreak.com/showthread.php?p=6307025#post6307025

RunRyder: Check out my RC Weather 'at a glance' proof-of-concept!
http://rc.runryder.com/helicopter/t781886p1/?p=6427847#RR

2015-02-07 features blurb posted to RunRyder:

o geolocation to use your current lat/lon
o search for zip codes
o much improved interface, including 'responsive' for small devices
o user-customizable ranges for precip, wind, temp, and clouds
o cloud cover now included
o tasty weather icons (can be disabled)
o url sharing that includes customized settings
o embed link for web masters
o tap/hover detail information for each hour (shows how the hour was rated)


** referenced apps/sites
** ! [Windalert](http://www.windalert.com/)
** ! [ETSU Observatory Clear Sky Chart](http://cleardarksky.com/c/ETSUObTNkey.html?1)
** [WindAlert iOS App] (https://itunes.apple.com/us/app/windalert/id317992025?mt=8)
** [Windalert](http://www.windalert.com/)
** [Meteogram weather widget](https://play.google.com/store/apps/details?id=be.inet.rainwidget)
   yellow for wind, blue bars for rainfall, and colour coded temperature
** [Windyty, wind forecast](https://www.windyty.com/spot/location/42.374/-72.518/name/Amherst?surface,wind,now,42.374,-72.264,11)
** [Aviation Weather Report and Forecast - Wind Speed, Temperature, Wind Direction, Precipitation Forecast](http://www.usairnet.com/cgi-bin/launch/code.cgi?state=TX&sta=KTKI)
** [meteocons](http://www.alessioatzeni.com/meteocons/res/img/screen.png)
** [1Weather:Widget Forecast Radar | 1mobile.com] (http://www.1mobile.com/1weather-widget-forecast-radar-336436.html)
** [windalert.com] (http://windalert.com/map#42.375,-72.513,10,1)


* v! set up forwarding to rc-weather.herokuapp.com <- www.peepweather.com
heroku domains:add example.com


** v! w/f DNS settings usually take up to 24 hours to propagate everywhere, so you may not be able to access your site immediately using your domain name.

** v what I did
*** v namecheap side
All Host Records:

    Host Name          IP Address/URL                  Record Type
    @                  http://peepweather.com          URL Redirect
    www                rc-weather.herokuapp.com        CNAME (alias)

Q: use 'http://' above? DEC: yes, per instructions below
Q: TTL: 1800? DEC: leave empty


*** v heroku side
https://dashboard.heroku.com/apps/rc-weather/settings
  Domain Names
     rc-weather.herokuapp.com
     www.peepweather.com


** REF: heroku
https://devcenter.heroku.com/articles/custom-domains


** REF: namecheap
https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-can-i-change-the-nameservers-for-my-domain
https://www.namecheap.com/support/knowledgebase/article.aspx/385

*** How do I setup a CNAME record?
It is possible to create a CNAME record if your domain is using Namecheap default DNS system. To do so: Choose ‘All Host Records’ on the left menu; type your domain (IE: www.yourdomain.com) into the IP Address/URL field of the @ line; select URL Redirect from the drop-down menu; enter the destination hostname as a value for WWW line and choose CNAME (Alias) as the record type; save changes.

via: http://wayback.archive.org/web/20131206153050/http://sergiotapia.me/2013/03/12/how-to-use-a-namecheap-domain-on-a-heroku-application

In the records settings page, you just need to point your domain to the Heroku servers. Your final settings should look like:

Host Name          IP Address/URL                  Record Type
@                  http://www.YOUR-DOMAIN.com      URL Redirect
www                heroku-app-name.herokuapp.com   CNAME (alias)

You’re done on the NameCheap side of configurations.


*** Using a Namecheap domain for a Heroku application
http://itsybitsybytes.com/using-a-namecheap-domain-for-a-heroku-application/

aha!


** hmm: The Limitations of DNS A-Records | Heroku Dev Center
https://devcenter.heroku.com/articles/apex-domains

avoid using DNS A-records and instead use a DNS provider that supports CNAME functionality at the apex, or use sub-domains exclusively.


* v move to own domain :-)
** v! decide and register domain name
DEC: peepweather.com ! (second choice: forecastpeek.com)
https://www.namecheap.com/cart/checkout/orderconfirmation.aspx?id=14574036
Your order 14574036, placed on Feb 03, 2015 05:52 PM is completed.

** v Q: start right away with subdomains?
rc.peepweather.com
bike.peepweather.com
cycle.peepweather.com
run.peepweather.com
tennis.peepweather.com
hunt.peepweather.com

+: prep for other audiences
-: extra step and more to remember for currently just one audience
-: rc.peepweather.com -> http://rc-weather.herokuapp.com
   but also need somewhere for www.peepweather.com to go :-/

DEC: wait on subdomains - use root domain


** v see [set up forwarding to rc-weather.herokuapp.com]


* v! embed feature for clubs' sites :-)
Have you considered an embed option for clubs to use that has a link to your site when clicked? For example, a club with 60 members regularly checks the club page for news, rules, ETC. They can always see the conditions for flight.

** maybe: todo
o share button that pops up copyable inputs
o maybe later: options (size, icons, etc), preview


** my thinking so far:
o iframe (simplest)
o /embed/ endpoint
  Q: or /forecast/embed? DEC: what else would I embed -> no forecast/
o pass zip plus all params, like current share url
o requires zip and all params, like current
o Q: size?

ex: http://www.peepweather.com/embed/77001?w=8|12&t=35|59|89|100&c=33|66&p=10|30


** learned from quick prototype:
o only want part of the page:
  o title, time, table
  o link at top to full page on my site ("Courtesy of __")
  o no popover, but maybe clicks -> full site

o not:
  o navbar, customize, share, debug, footer
  o Q: include key?


o would be nice: share button with popup to configure
  o show configured url and preview
  o options: iframe size, whether to show colors & icons key, show icons
  o set table size! maybe large/normal and small (scaled down) choices


** v https://www.youtube.com/watch?v=nTgJJy3Umhw
generates a full HTML document with own style sheet
link to original on site
scripts

Share > Embed
<iframe width="560" height="315" src="https://www.youtube.com/embed/nTgJJy3Umhw" frameborder="0" allowfullscreen></iframe>


** https://www.google.com/maps/place/Amherst,+MA/@42.3676145,-72.505491,12z/data=!3m1!4b1!4m2!3m1!1s0x89e6ce020a71240f:0xd5751d15974c2fdc
Share > Embed

<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d94330.33116468109!2d-72.50549095000001!3d42.3676145!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89e6ce020a71240f%3A0xd5751d15974c2fdc!2sAmherst%2C+MA!5e0!3m2!1sen!2sus!4v1423275410144" width="600" height="450" frameborder="0" style="border:0"></iframe>

has a dropdown: Small, Medium, Large, Custom size

gives a popup preview


** ~ http://www.wunderground.com/stickers/?query=01002
click link to pop up image and code
aha: span not iframe - dynamic image
click opens full site in new window

<span style="display: block !important; width: 180px; text-align: center; font-family: sans-serif; font-size: 12px;"><a href="http://www.wunderground.com/cgi-bin/findweather/getForecast?query=zmw:01002.1.99999&bannertypeclick=wu_bluestripes" title="Amherst, Massachusetts Weather Forecast" target="_blank"><img src="http://weathersticker.wunderground.com/weathersticker/cgi-bin/banner/ban/wxBanner?bannertype=wu_bluestripes&airportcode=KCEF&ForcedCity=Amherst&ForcedState=MA&zip=01002&language=EN" alt="Find more about Weather in Amherst, MA" width="160" /></a><br><a href="http://www.wunderground.com/cgi-bin/findweather/getForecast?query=zmw:01002.1.99999&bannertypeclick=wu_bluestripes" title="Get latest Weather Forecast updates" style="font-family: sans-serif; font-size: 12px" target="_blank">Click for weather forecast</a></span>

<span style="display: block !important; width: 180px; text-align: center; font-family: sans-serif; font-size: 12px;"><a href="http://www.wunderground.com/cgi-bin/findweather/getForecast?query=zmw:01002.1.99999&bannertypeclick=wu_travel_landmarks1" title="Amherst, Massachusetts Weather Forecast" target="_blank"><img src="http://weathersticker.wunderground.com/weathersticker/cgi-bin/banner/ban/wxBanner?bannertype=wu_travel_landmarks1&airportcode=KCEF&ForcedCity=Amherst&ForcedState=MA&zip=01002&language=EN" alt="Find more about Weather in Amherst, MA" width="160" /></a><br><a href="http://www.wunderground.com/cgi-bin/findweather/getForecast?query=zmw:01002.1.99999&bannertypeclick=wu_travel_landmarks1" title="Get latest Weather Forecast updates" style="font-family: sans-serif; font-size: 12px" target="_blank">Click for weather forecast</a></span>


** x https://twitter.com/richarddawkins
pops up code, preview
aha: quote + script
looks plain embedded

<blockquote class="twitter-tweet" lang="en"><p>Incredibly, it seems there are many people out there who honestly think quoting their own holy book at you is a clinching argument-winner.</p>&mdash; Richard Dawkins (@RichardDawkins) <a href="https://twitter.com/RichardDawkins/status/563652904524185601">February 6, 2015</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>


** REF
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe


Using inline frames (iframe elements) to embed documents into HTML documents
http://www.cs.tut.fi/~jkorpela/html/iframe.html

inline frame (floating frame) .. Technically, an iframe element is a text-level element, or "inline element" (as opposite to block-level elements). Syntactically an iframe element may occur inside a paragraph, even between two words of text

<iframe src="news.html" width="40%" height="80" align="right"> <p>See our <a href="news.html">newsflashes</a>.</p> </iframe>


