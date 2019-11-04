import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
import statsmodels.api as sm
import re

# Function to extract numbers like "2.0" from a string with 
# numbers and letters in it, e.g. "2.0K"
# ... for example, the monetary amounts in the 
#     damage_property or damage_crops columns
def get_num( string):
	v = re.findall(r'(\d*\.\d+|\d+)', string)
	if len(v) == 0:
		return 0.0
	else:
		return v[0]

# Function to convert "2.0K" to 2000.0
def convert_num( x):
	if type( x ) is float:
		if x == np.nan:
			return 0.0
		else:
			return x
	else:
		if ( x == '' or x == 'NaN'):
			return 0.0
		else:
			x = str(x)
			num_str = get_num(x)
			num = float(num_str)
			if x.find('K') != -1:
				num = num*1000.0
			if x.find('M') != -1:
				num = num*1000000.0
			if x.find('B') != -1:
				num = num*1.0e9
			return num

# Creates a simple data frame of 2 vars, of sum of cols, 
def regroup_by_x( df, group_x, col1, col2):
	
	# Plot property and crop damage by year
	c1_vs_x  = df.groupby(group_x)[col1].sum()                 
	c2_vs_x  = df.groupby(group_x)[col2].sum()                    
	c1vx = pd.DataFrame({group_x : c1_vs_x.index, \
			                col1: c1_vs_x.values})              
	c2vx = pd.DataFrame({ group_x  : c2_vs_x.index, \
			                col2: c2_vs_x.values})                  
	cost = pd.merge(c1vx, c2vx, on=group_x)                                           
	return cost	                                    
	
																				
### Collect similar events into broad categories
def collect_events( event ):
	TropicalSystems = ["Marine Hurricane/Typhoon", \
						"Marine Tropical Depression", \
			        	"Marine Tropical Storm", \
						"Tropical Depression", \
						"Tropical Storm", \
						"Hurricane (Typhoon)", \
						"Hurricane"]

	WindEvents = [	"Heavy Wind", \
					"Marine Strong Wind", \
					"Marine High Wind", \
					"High Wind", \
					"Strong Wind"]

	Flood = [ 	"Lakeshore Flood", \
				"Flood", \
				"Flash Flood", \
				"Coastal Flood"]

	Winter = [	"High Snow", \
				"Heavy Snow",\
				"Freezing Fog", \
				"Sleet", \
				"Cold/Wind Chill", \
				"Winter Weather", \
				"Frost/Freeze", \
				"Lake-Effect Snow", \
				"Winter Storm", \
				"Ice Storm", \
				"Avalanche", \
				"Extreme Cold/Wind Chill", \
				"Blizzard"]
	
	Tornados = [	"Tornado", \
					"Waterspout", \
					"Funnel Cloud"]

	TStorms = [	"Thunderstorm Wind", \
				"Marine Thunderstorm Wind",\
				"Lightning",\
				"Hail", \
				"Marine Hail", \
				"Marine Lightning"]

	Slides = [	"Avalanche", \
				"Debris Flow", \
				"Landslide"]

	OceanSwell = [	"Tsunami", \
					"Sneakerwave", \
					"High Surf", \
					"Storm Surge/Tide", \
					"Coastal Flood", \
					"Rip Current", \
					"Astronomical Low Tide"]
	
	DroughtDust = ["Drought", \
					"Dust Storm", \
					"Dust Devil"]

	Heat = [ "Excessive Heat", \
			 "Heat"]

	VolcanicAsh = ["Volcanic Ashfall", \
					"Volcanic Ash"]

	FogSmoke = ["Marine Dense Fog", \
				"Dense Fog", \
				"Dense Smoke"]

	Misc = ["Northern Lights", \
			"Seiche", "OTHER"]
	

	if event in TropicalSystems:
		return "Tropical Systems"
	if event in WindEvents:
		return "Wind Events"
	if event in Flood:
		return "Flood"
	if event in Winter:
		return "Winter Weather"
	if event in Tornados:
		return "Tornadic event"
	if event in TStorms:
		return "Thunderstorms"
	if event in Slides:
		return "Landslide/Avalanche"
	if event in OceanSwell:
		return "Coastal waves"
	if event in DroughtDust:
		return "Drought or dust"
	if event in Heat:
		return "Heat"
	if event in VolcanicAsh:
		return "Volcanic Ash"
	if event in FogSmoke:

		return "Miscellaneous"
	else:
		return event
	return event

def histogram_damage( df, damage, tit, filename): 
	plt.clf()
	plt.cla()
	plt.close()
	ect = df.groupby("EVENT_CATEGORY").sum()[damage] 
	ect = ect.sort_values()
	print(ect)
	axes = plt.gca()
	ymin = ect.min()
	ymax = ect.max()*1.1
	axes.set_ylim([ymin, ymax])
	f = ect.sort_values().plot(kind='bar') 
	f.set_title(tit)
	plt.gcf().subplots_adjust(left = 0.15, bottom = 0.4)
	plt.savefig(filename)

	return 

# For a givent category in a reduced dataframe 
# e.g. "FLOOD_CAUSE" in a floods-only dataframe or
#      "TOR_F_SCALE" in a tornadoes-only dataframe
# creates a new column in dataframe for each different value
# that category, and stores 1 if category[i] == value, or 0 if != value

def qual_columns(df, category):
	count = len(df[category].value_counts())
	ser = df[category].value_counts()
	for val in ser.index:
			df[val] = df[category].apply(lambda x: 1 if x==val else 0)
	return df


def fujita_concat( rating):
	if rating == "F0" or rating == "EF0":
		return 0
	if rating == "F1" or rating == "EF1":
		return 1
	if rating == "F2" or rating == "EF2":
		return 2
	if rating == "F3" or rating == "EF3":
		return 3
	if rating == "F4" or rating == "EF4":
		return 4
	if rating == "F5" or rating == "EF5":
		return 5
	else:
		return -1


def Is_it_old_F( rating):
	Fujita_scale = ['F0', 'F1', 'F2', 'F3', 'F4', 'F5']
	if rating in Fujita_scale:
		return True
	else:
		return False

def tornado_lin_model(df, x_col, y_col, mod_file, pltfile):
	
	X = df[x_col]
	X = sm.add_constant(X) # sns doesn't automatically include intercept
	y = df[y_col]
	mod = sm.OLS(y,X).fit()
	mf = open(mod_file, 'w')
	mf.write('Fujita scale linear model: '+ x_col+', '+ y_col )
	mf.write(mod.summary().as_csv())
	mf.close()
	plt.clf()
	plt.cla()
	plt.close()
	line_x = np.arange(0, 6)
	p = mod.params
	ax = df.plot( x = x_col, y = y_col, kind = 'scatter')
	ax.plot( line_x, p.const + p[x_col] * line_x)
	plt.savefig( pltfile )
	return


