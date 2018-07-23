import sys
import glob
import math
import scipy
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

# Load Storm Event detail files for 1996-2018 
# These are the years for which the complete storm events data exists



path = r'details/1996-2018/'
allFiles = glob.glob(path + "*.csv")
df = pd.DataFrame()
list_ = []
for file_ in allFiles:
	frame = pd.read_csv(file_, index_col=None, header = 0, low_memory=False)
	list_.append(frame)

df = pd.concat(list_)
# frame is a dataframe with 1,253,244 rows, 51 columns
df.head()

# Function to convert numbers like "2.0K" to "2000.0"
# ... for example, as for the monetary amounts
#     in the columns damage_property or damage_crops
def get_num( string):
	v =  re.findall(r'(\d*\.\d+|\d+)', string)
	if len(v) == 0	# There is a typo in the 1999 data, where a cost is input:
		return 0.0	# as just "K".  Convert this to $0.0
	else:
		return v[0]

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
			num_str = get_num(x)
			num = float(num_str)
			if x.find('K') != -1:
				num = num * 1000.0
			if x.find('M') != -1:
				num = num*1000000.0
			return num

# Now, convert DAMAGE_PROPERTY and DAMAGE_CROPS columns to all real float values
df['DAMAGE_PROPERTY'] = df['DAMAGE_PROPERTY'].apply(convert_num)
df['DAMAGE_CROPS']    = df['DAMAGE_CROPS'].apply(convert_num)
df['DAMAGE_PROPERTY'] =df['DAMAGE_PROPERTY'].fillna(0)
df['DAMAGE_CROPS']    =df['DAMAGE_CROPS'].fillna(0)

# Total Property Damage and Crop Damage costs by year:
 
total_prop_vs_yr  = df.groupby('YEAR')['DAMAGE_PROPERTY'].sum()
total_crop_vs_yr  = df.groupby('YEAR')['DAMAGE_CROPS'].sum()
tPvy = pd.DataFrame({"Year":total_prop_vs_yr.index, \
				"Total Property Damage": total_prop_vs_yr.values})
tCvy = pd.DataFrame({"Year":total_crop_vs_yr.index, \
				"Total Crop Damage": total_cprop_vs_yr.values})
cost = pd.merge(tPvy, tCvy,on='Year')

# Plot Property Damage cost and Crops cost vs Year.
f = cost.plot(x='Year', y=['Total Property Damage', 'Total Crops Damage'],\
				title = 'Total Weather Costs vs Year')
plt.savefig('Cost_per_year.pdf')
# There is no apparent trend, although a linear regression may find some minor
# trend.  More interestingly, the cost of Property damage and Crop damage seem 
# only somewhat correlated-- Future questions: how well are they correlated?
# Are they correlated more strongly due to certain types of weather?

# Figure 2.  To start examining this question, break down the cost by type of 
# weather event.  So, as a first trial, compare how costs compare for hail 
# damage.  

type_of_event = df.groupby('EVENT_TYPE')

def cost_compare( event_type, toe_df):
	dataframe = toe_df.get_group( event_type )
	pvy_sums = dataframe.groupby('YEAR')['DAMAGE_PROPERTY'].sum()
	cvy_sums = dataframe.groupby('YEAR')['DAMAGE_CROPS'].sum()
	pvy = pd.DataFrame({"Year": pvy_sums.index, "Total Property Damage": pvy_sums.values})
	cvy = pd.DataFrame({"Year": cvy_sums.index, "Total Crop Damage": cvy_sums.values})
	cost = pd.merge( pvy, cvy, on="Year")
	return cost

hail_cost = cost_compare("Hail", type_of_event)
f2 = hail_cost.plot(x="Year", y=["Total Property Damage", "Total Crop Damage"],\
				title = "Hail Costs vs Year")
plt.savefig("hail_vs_year.pdf")

# Note: While the total costs of all weather related damage appear 
# to be potentially correlated, that may not be the case for specific types
# of weather.  This makes sense on an obvious level: for example, Marine High
# winds are not likely to cause much crop damage.  So one big question is, which 
# types of damage are highly correlated, and how much of an effect do they 
# cause? Which of these are more tightly tied to the fatalities? And how
# does the cost and fatality rate for similar events vary by state/county/zone?
# Do unseasonable events cause more damage?



