# StormEventsDataProject
Examining the NOAA Storm Events Database for the human costs of weather.  The current model examines the 
storm event details from 1996-2018, as prior data did not include most types of storm event.  Future analysis 
will try to incorporate location and specific fatality information to improve models.  In addition, population
census data would be valuable for evaluating relative risk.

Data pre-cleaning:  In order to examine the financial costs of individual storm events, the DAMAGE_PROPERTY and 
DAMAGE_CROPS columns need to be cleaned up.  They are currently input in the form "100.0", "2.5K", ".2B". 
The function functions.convert_num( x) converts a string of any of these forms into a float value.

Note: None of these evaluations incorporate inflation yet.

----------------------------------------------------------------------------------------------------------------
1.  Are deaths, injuries, or financial costs correlated with one another over a year?

Using a Pearson correlation table to compare property damage, direct deaths, and direct injuries vs year, 
it looks like property damage is essentially uncorrelated with deaths or injuries.  Injuries and deaths are
slightly more correlated with each other, but still not strongly.

                 | DAMAGE_PROPERTY   | DEATHS_DIRECT  |  INJURIES_DIRECT
-----------------|-------------------|----------------|------------------
DAMAGE_PROPERTY  |       1.000000    |   0.030077     |    0.084751


DEATHS_DIRECT    |       0.030077    |   1.000000     |    0.168151
INJURIES_DIRECT  |       0.084751    |   0.168151     |   1.000000

See also: "Death_inj_by_yr.pdf", a plot of total direct deaths and direct injuries vs. year

* Take Away:  Reducing deaths, injuries, and property damage likely will each require different strategies, 
              which ideally will become apparent upon a deeper dive into the data.
  
--------------------------------------------------------------------------------------------------------------------------------
2.  Which types of events are the most costly/injurious/deadly every year?  

For this analysis, it's beneficial to categorize the different event types into related categories. In part, this is because 
some of the categories are nearly indistinguishable or are extremely closely related.  For example, the categories "Hurricane" 
and "Hurricane/Typhoon" describe identical weather phenomena.  But in addition, there are 61 listed categories, many of which 
are closely related.  The function functions.collect_events( event) takes an EVENT_TYPE string and classifies it into one of 
my defined categories.  So, for example, a Tropical Depression would be classified in "Tropical Systems", while an Ice Storm 
would fall in the category "Winter Weather".

Simple histograms comparing event categories for property damage ("total_money_hist.pdf"), direct deaths ("total_death_hist.pdf"), 
and direct injuries ("total_inj_hist.pdf") reveal which event categories cause the most of each type of damage. I have ignored 
crop damage for simplicity here (crop damage is not strongly correlated with property damage, so it is another independent 
form of damage that could be examined).  I have also ignored indirect deaths and indirect injuries, as this data has only begun
to be taken starting in 2005, so it's difficult to compare pre-2005 data to post 2005 data, and it's unknown how indirect deaths
and injuries are counted (if they are at all) in the pre-2005 data.  So, for this analysis, I assume that indirect deaths prior to 
2005 are simply not recorded at all in the data.

* Take Away:  
Top 3 Worst events per damage type
Property damage:  Tropical systems ( $1.47e11), Floods ( $1.44e11), Coastal Waves, i.e. storm surge, coastal flood, tsunami ( $5.5e10)
Direct Deaths: Heat (2815), Flood (1971), Tornado (1742)
Direct Injuries:  Tornado (24,493), Heat (15,364), Thunderstorms (12,012)


--------------------------------------------------------------------------------------------------------------------------------
3.  Linear models of various major categories.  How are the costs (deaths, injuries, property damage) related to more detailed
specifiecs about the event type?
                             ------------- ------------- ------------- ------------- -------------
3a)  How does the cost of a flood relate to the flood's cause?  Does knowing the cause of the flood provide any help in predicting
the cost of the flood?

For this, I used a basic linear model to predict costs.  Each type of flood cause was assigned a boolean variable (1 or 0), with
the model taking the form:
      /hat{y} = \beta_0 + \beta_1*X + ... + \beta_6 * X
      
There are 7 different classifications of flood cause, so 6 dummy variables are needed in addition to the linear constant (\beta_0).

How good is the model?  Here's a brief summary of the model statistics:
                       R^2    F-statistic     P(F-statistic)
Property damage       0.001      4.471          0.000157  
Direct deaths         0.001      6.433          8.69e-7
Direct injuries       0.001      0.1232         0.994  
 
Take away:  Property damage and deaths are weakly preditable based on the flood cause, but the model isn't exceptionally strong.
            The model for direct injuries is no better than the null hypothesis-- in other words, knowing the flood cause tells you 
            nothing about the number of injuries.
                             ------------- ------------- ------------- ------------- -------------
3b) What about tornadoes vs. the Fujita scale?  In looking at the Fujita scale, there was a redefinition of the criteria used to 
determing the Fujita scale from the Fujita scale to the Enhanced Fujita scale in 2007.  The tornado categorizations are roughly
equivalent for both versions of the scale, however.  So for a first analysis, I'll simply assume F0 ~ EF0, etc...  The term 'EFU' 
appears several times in the data, but is not defined in the documentation (and a simple Google search didn't reveal this as
a standard term), so I have assumed it means "Enhanced Fujita Unknown", so these specific data points have been thrown out.

For simplicity, we assume F0 == EF0 --> 0, F1 == EF1 -->1, etc.  The Fujita wind scale is not perfectly linear, but it is roughly 
linear in wind speed, so this is a reasonable approximation for this noisy data set.

The model for property damage cost is strongly expected to correlate with the Fujita scale, since the Fujita scale assignment for
a given tornado is made by examining the worst damage caused by the tornado within a given area.  So, for example, an tornado
which completely removes sturdy brick homes from their foundations with no trace will be classified as an F5 or EF5 tornado based on 
laboratory studies of potential wind-speed damage.  So it's naturally expected that total financial damage should be relatively simply 
modeled by the Fujita scale, which is essentially a measure of maximum local physical property damage.  But since the F-scale isn't 
actually  direct measure of financial cost (and especially not of deaths or injuries), so this linear model is still reasonable.

                       R^2    F-statistic     P(F-statistic)
Property damage       0.018      563.2          2.29e-123  
Direct deaths         0.031      974.9          1.13e-210
Direct injuries       0.040      1260           1.68e-270
* likewise, \beta_0 and \beta_1 have very tiny (<0.000) p-values.

                             ------------- ------------- ------------- ------------- -------------
3c.  Because the Fujita scale was updated in 2007 to reflect improved information about damage caused by wind, it's natural to ask...
Does the Enhanced Fujita scale do a better job of predicting the damage data than the older Fujita scale?

Property damage     R^2    F-statistic     P(F-statistic)
Old Fujita Scale    0.55      833.7          8.58e-189
Enh. Fujita         0.019     300.9          9.23e-67

Deaths              R^2    F-statistic     P(F-statistic)
Old Fujita Scale    0.054     864.1          9e-185
Enh. Fujita         0.030     472.2          3.97e-103

Injuries            R^2    F-statistic     P(F-statistic)
Old Fujita Scale    0.086     1432           1.48e-299
Enh. Fujita         0.031     479.9          9.21e-105

Take away:  Surprisingly, the new Enhanced Fujita scale doesn't do a better job than the old one!  This warrants further investigation:
maybe outlier events (e.g. the Joplin tornado) are having a stronger effect on the linear model than might be expected.  It's also 
possible that improved weather forcasting and/or improved building construction has reduced the correlation between tornado
strength and building cost.  

