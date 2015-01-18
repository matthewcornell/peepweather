### Introduction

This is a simple web app to display outside weather conditions in an 'at a glance' format where each hour is a cell
that is 'stoplight' color coded based on how good it appears for activities like RC flying.


### To Do

- color key -> template used in list and cal
- don't show column if all white b/c non-white only in unshown hours (night)
- show why color chosen - tooltip?
- debug link to data URL (lat, lon)
- page titles include name

- do smarter: filter out according to daylight (don't show if dusk or night)
- index:
    - forms for entering zip, and for entering query
    - eventually a form to set color ranges for parameters
- overall summary
- geolocation
- change Hour.color() to give numerical rating to each variable, then sum to get final. any red would have to override
  result, though
- make pretty :-)
- ...
