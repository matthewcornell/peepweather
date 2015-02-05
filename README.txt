;; -*- mode: outline -*-

* >> bugs
** 1 navbar: banner too tall for mobile?

** 2 sunrise/set off by an hour? current: twilight = -12 * ephem.degree
http://stackoverflow.com/questions/26501745/how-to-determine-if-it-is-daytime-light-outside-in-python-using-ephem-library
http://rhodesmill.org/pyephem/rise-set.html#computing-twilight
http://stackoverflow.com/questions/2637293/calculating-dawn-and-sunset-times-using-pyephem
fred.horizon = '-6' #-6=civil twilight, -12=nautical, -18=astronomical

** 3 responsive: when key goes below table, it stretches full width. problem?

** ? don't show first column if all white

** ? cookies: use secure?

* >> features: to do
** 1 add chick pic image in header!
was causing problems - mobile navbar to cover top of content, etc.

** 1 text input error-checking (and forgiveness, validation)
o zip/latlon:
  o validation: not empty. zip or lat/lon pattern (zip: five numbers, exists in zipcode file)
  o trip spaces around comma, ends
  o bug: empty -> Not Found

o search:
  o not empty, matches zipcode file. ideally: completion
  o trim space from ends
  o bug: empty -> Not Found

o ranges : param values: not empty. ints. sorted

** 1 "Colors & Icons": switch Medium and Low columns, so that the medium column is to the left and low is to the right?
And maybe add a title above that chart: "Desirability:" currently it's slightly confusing (until seeing "how it works" link).

"Low" and a wind icon would, not knowing otherwise" mean low wind, where in this context it means low desirability to fly, right? Maybe "Light" and "Heavy" would be better terms for the gen pop.... Doesn't sound right either, but point remains...

** 1 mobile: tap for pop up detail (can't hover)

** 2 search: decide what I want it to do
whole state name. completion. sort by name

** 2 rethink default ranges
Slyster suggests temp:

<35 = poor
35-59 = medium
60-89 = great
>90 = medium

** 3 use jQuery everywhere

** continue: ads, subdomains, etc.

** when good enough -> announce
rc sites, clubs, etc.


* features: someday/maybe
** favorite flying locations :-)
add my favorite locations to a list, and have that list saved for when I come back to the page

** recently found - last 5 or so :-)

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
[Helifreak: Check out my RC Weather 'at a glance' proof-of-concept!](http://helifreak.com/showthread.php?p=6307025#post6307025)

[RunRyder: Check out my RC Weather 'at a glance' proof-of-concept!](http://rc.runryder.com/helicopter/t781886p1/?p=6427847#RR)


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

