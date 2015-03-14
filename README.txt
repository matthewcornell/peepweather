;; -*- mode: outline -*-

* refactoring
** move timezone normalization from Forecast.hoursAsCalendarRows() to WeatherGovSource.makeHours()

** titles: write Forecast method to help zipOrLatLon. use in stickers.html too

** embed code: make it a template like stickers.html

** change {% set %} to {% with %}
http://flask.pocoo.org/docs/0.10/patterns/flashing/

** Make Heroku run non-master Git branch - Stack Overflow
http://stackoverflow.com/questions/14593538/make-heroku-run-non-master-git-branch/14593582?noredirect=1#comment45877147_14593582

 @MatthewCornell branch-remote/master doesn't have to be the same branch as origin/master, so the suggestion in this answer works well (that is, git push branch-remote branch:master) and you don't have to merge into origin/master. I do wish Heroku would let you specify deploy branch as a config setting, but this isn't a bad alternative. –  Marnen Laibow-Koser Mar 2 at 2:10 


* bugs
** ~ make screen shot on main page clickable :-)

** ~ bottom line of table flashes darker when popover shows

** ~ 404 not found: http://127.0.0.1:5000/assets/js/ie10-viewport-bug-workaround.js

** ~ appearance (responsive): when key goes below table, it stretches full width

** ? sunrise/set off by an hour? current: twilight = -12 * ephem.degree
http://stackoverflow.com/questions/26501745/how-to-determine-if-it-is-daytime-light-outside-in-python-using-ephem-library
http://rhodesmill.org/pyephem/rise-set.html#computing-twilight
http://stackoverflow.com/questions/2637293/calculating-dawn-and-sunset-times-using-pyephem
fred.horizon = '-6' #-6=civil twilight, -12=nautical, -18=astronomical


* features: to do
** Forecast > Share: consolidate into tabs or popup? (getting cluttered)

** overview/summary :-)
"Looks like the best times are __, __, and __."
"The best days to get out look to be ..."

** stickers: later
o editor customize appearance (size, format, include summary, etc.)
o summary for the coming day/week - "Looks like the best times are __, __, and __."

http://www.wunderground.com/stickers/?query=Amherst,%20Massachusetts
http://www.wunderground.com/stickers/classic.html?query=Amherst,%20Massachusetts

** use jQuery everywhere


* features: to consider
** ? add activity popup menu for turn-key parameter settings?

** ~ fog

** activity-based profiles selectable from list
e.g., skiing - don't mind coder, windier

** ~ replace message.html with modal?

** ~ in-place form as service to webmaster visitors
user enters zip, form refreshes in-place
like: http://www.107thrc.com/

I suppose you'd have a URL (or a special query string parameter) that instead of parsing the zip from the path it would display an input control prompting for zip. After entering the zip it would post back, the rest of the settings from the query string would apply and the grid would display. Without adding the zip to a cookie it would make the zip stateless, so a page refresh would necessitate entering the zip again. But at least it wouldn't be locked down to a single zip for cases like Rick is describing. If you did add the zip to the cookie it could lock it there for a user, but you'd probably want another button on the grid page to allow you to enter another zip.

REF:
http://www.codeproject.com/Questions/635541/reloading-a-div-on-a-button-click-using-Jquery-or
http://www.extremetechblog.com/refresh-div-without-reloading-page/
http://community.sitepoint.com/t/refresh-div-content-without-reloading-page/5353
http://www.coderanch.com/t/526538/HTML-CSS-JavaScript/refresh-DIV
http://crunchify.com/how-to-refresh-div-content-without-reloading-page-using-jquery-and-ajax/
http://stackoverflow.com/questions/7175038/how-to-reload-a-div-without-reloading-the-entire-page
http://stackoverflow.com/questions/7218070/reload-contents-of-div-using-javascript
http://www.kavoir.com/2009/01/using-javascript-to-refresh-and-reload-an-iframe-on-main-page.html

** recently found - last 5 or so :-)

** ~ nice PIL fonts instead of current blocky one?
would probably fix this: sticker 'T' column headings are cut off on the left

REF:
http://www.geeks3d.com/20131108/beginning-with-pillow-the-pil-fork-python-imaging-library-tutorial-programming/7/
http://stackoverflow.com/questions/12384838/using-fonts-in-pil-without-freetype
http://stackoverflow.com/questions/19337952/how-to-prepare-a-freetype-pil-pillow-package-for-heroku-and-django?lq=1
http://stackoverflow.com/questions/12384838/using-fonts-in-pil-without-freetype/12388342#12388342
http://stackoverflow.com/questions/619618/using-pixel-fonts-in-pil

** ~ don't show first column if all white?

** ~ user accounts so that settings follow user around on every computer

** ~ favorite flying locations (like bookmarks)
add my favorite locations to a list, and have that list saved for when I come back to the home page

It could be as simple as a dropdown list somewhere. For example, a small drop down list in the header next to settings or something. It doesn't even need to have a title; an icon that represents favorites would be fine. You could then show a text hint when hovered over, or simply have it be at the top of the pop-up before your list of favorites.

I'd personally rather have one bookmark to get to all the places I care about instead of one for each location. (OK, I've only got two so far, but, hey, that could always change... )

** ~ daylight: add new setting for defining which hours to show - start, end (inclusive), rather than hard-coded

** ~ a checkbox controlling whether apparent or actual temp is used

** ~ editable parameter weights for combined importance to the final rating


** ~ editable graph via http://jsxgraph.uni-bayreuth.de/wp/ :-)
user can drag points around to edit


** ~ change terminology - confusion over Low/Med/High: desirability vs. amount
o low rain vs. low desirability - high rain
o Low means Low Desirability (like Orange or Red) not low amounts of clouds

-> It might help to change the terms from Low, Medium, High to something like Bad, OK, and Great (or anything else that is more easily understandable without explanation).


* future: major features
** international. I don't know the details myself, but drop Benny Wydooghe a line on google+, or in the Meteogram Widget
group on google+. He's the developer of the widget I posted a screenshot of earlier, and has a great international weather service he uses. He's had to work through all these timezone issues, provider issues, etc himself so he'd  probably be a good contact for you. - http://helifreak.com/showpost.php?p=6317185&postcount=89

** mobile app
o widget
o alerts: mobile app that alerts me when local conditions are "green"
o the integrate it with the existing android/iOS calendars (shade the background of your calendar's hourly blocks with flying condition colors). could see my actual appointments etc while being able to see flying conditions at a glance (and schedule everything for red times!)


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


