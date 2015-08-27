# peepweather
This is the code for [PeepWeather](http://peepweather.com) . From index.html:

## What is PeepWeather?
PeepWeather is a web application that shows a color-coded traffic light view of the weather for the next seven days, hour-by-hour. In one glance you can quickly see how nice it looks outside for the coming week, and plan accordingly.

## Who is it for?
Whatever we do outdoors - sports, yard work, hobbies, etc. - we all need to know the weather to decide when it'll be nice for our outside fun. The problem is we're busy, and other forecast sites make us work too hard to figure out what we really care about: a go/no go for each precious hour.

## Why use it?
Unlike most weather sites that either provide too little hourly information or way too much, PeepWeather makes it easy for you to tell, in one look, how the week is stacking up. Lots of red? Relax indoors. Tons of green? Enjoy life outside!


# Installing
See requirements.txt, mainly [Flask](http://flask.pocoo.org/), [PyEphem](http://rhodesmill.org/pyephem/), and 
[Pillow](https://github.com/python-pillow/Pillow). Virtualenv is recommended.


# Running
App: This is a [Flask](http://flask.pocoo.org/) app, so just:

    $ cd <your repos>/rc-weather-flask
    $ source ~/virtualenvs/<your venv>/bin/activate
    $ python run.py
  
Tests: Standard [unittest](https://docs.python.org/3.3/library/unittest.html) tests:

    $ python -m unittest discover
    
(NB: This output is expected: "error getting data for zipOrLatLon Location('01002')".) :


# Code tour
TBD


# TODO's
See todo.txt (Emacs outline format)
