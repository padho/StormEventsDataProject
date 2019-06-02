# StormEventsDataProject
Examining the NOAA Storm Events Database for the human costs of weather.  The current model examines the 
storm event details from 1996-2018, as prior data did not include most types of storm event.  Future analysis 
will try to incorporate location and specific fatality information to improve models.  In addition, population
census data would be valuable for evaluating relative risk.

Data pre-cleaning:  In order to examine the financial costs of individual storm events, the DAMAGE_PROPERTY and 
DAMAGE_CROPS columns need to be cleaned up.  They are currently input in the form "100.0", "2.5K", ".2B". 
The function functions.convert_num( x) converts a string of any of these forms into a float value.

Note: None of these evaluations incorporate inflation yet.

-----

## 1. Scrape

First, run `python scrape.py` to scrape the .csv files from the NOAA Storm Events Database into project 
home folder. The .csv files will be stored in 3 folders: /details, /fatalities, /locations

## 2. Clean 


