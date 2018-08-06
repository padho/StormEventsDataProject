import sys
import glob
import math
import scipy
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import statsmodels.api as sm

import functions


def LoadFile( ):
	path = r'details/1996-2018/'
	allFiles = glob.glob(path + "*.csv")
	df = pd.DataFrame()
	list_ = []
	for file_ in allFiles:
		frame = pd.read_csv(file_, index_col=None, \
						header = 0, low_memory = False)
		list_.append(frame)
	df = pd.concat(list_)
	return df
	

def main():
	
	# Load files for storm details, 1996-2018	
	df = LoadFile()

	print(df.head())
		
	# Convert DAMAGE_PROPERTY and DAMAGE_CROPS columns to real float values
	df['DAMAGE_PROPERTY'] = df['DAMAGE_PROPERTY'].apply(functions.convert_num)
	df['DAMAGE_PROPERTY'] = df['DAMAGE_PROPERTY'].fillna(0)
	df['DAMAGE_CROPS'] = df['DAMAGE_CROPS'].apply(functions.convert_num)
	df['DAMAGE_CROPS'] = df['DAMAGE_CROPS'].fillna(0)
	
	# Get the total property damage, crop damage, injuries, direct fatalites
	# and indirect fatatlities by year
	# column_cost_list = all cols that document money or human costs:
	column_cost_list = ['DAMAGE_PROPERTY', 'DAMAGE_CROPS', 'INJURIES_DIRECT', \
				 'INJURIES_INDIRECT', 'DEATHS_DIRECT', 'DEATHS_INDIRECT']
	
	# Merge monetary columns, injuries columns, and deaths columns:
	money_vs_yr = functions.regroup_by_x( df, 'YEAR', 'DAMAGE_PROPERTY', \
					'DAMAGE_CROPS')
	injury_vs_yr = functions.regroup_by_x( df, 'YEAR', 'INJURIES_DIRECT', \
					'INJURIES_INDIRECT')
	death_vs_yr = functions.regroup_by_x( df, 'YEAR', 'DEATHS_DIRECT', \
					'DEATHS_INDIRECT')
		
	# Plot total costs vs. year:
	f1 = money_vs_yr.plot( x = 'YEAR', y = ['DAMAGE_PROPERTY', 'DAMAGE_CROPS'])
	f1.set_xlabel('Year')
	f1.set_ylabel('US dollars')
	f1.set_title('Total financial damage by year')
	plt.savefig('total_cash_by_yr.pdf')
	
	f2 = injury_vs_yr.plot( x = 'YEAR', y = ['INJURIES_DIRECT',\
					'INJURIES_INDIRECT'])
	f2.set_xlabel('Year')
	f2.set_ylabel('Injuries')
	f2.set_title('Total injuries by year')
	plt.savefig('injuries_by_yr.pdf')


	f3 = death_vs_yr.plot( x = 'YEAR', y = ['DEATHS_DIRECT',\
					'DEATHS_INDIRECT'])
	f3.set_xlabel('Year')
	f3.set_ylabel('Deaths')
	f3.set_title('Total deaths by year')
	plt.savefig('deaths_by_yr.pdf')

	###  It looks like indirect injuries and deaths only started being
	###  recorded in 2006 (both == 0 before 2006)
	###  combine the two categories for total deaths...

	df["DAMAGE"] = df["DAMAGE_PROPERTY"] + df["DAMAGE_CROPS"]
	df["DEATHS"] = df["DEATHS_DIRECT"] + df["DEATHS_INDIRECT"]  
	df["INJURIES"] = df["INJURIES_DIRECT"] + df["INJURIES_DIRECT"]
	### Now, categorize event types into broader categories
	###   to see what the cumulative total cost
	
	df["EVENT_CATEGORY"] = df["EVENT_TYPE"].apply(functions.collect_events)
	functions.histogram_damage(df, "DAMAGE", \
					"Total fiscal damage by category (1996-2018)", \
					"total_money_hist.pdf")
	functions.histogram_damage(df, "INJURIES",\
					"Total injuries by category (1996-2018)", \
					"total_inj_hist.pdf")
	functions.histogram_damage(df, "DEATHS", \
					"Total deaths by category (1996-2018)", \
						"total_death_hist.pdf")

	### Can storm events for winter weather be used to predict/model
	### other events in same year?
	# Start by counting winter events of each category per year 
	#  --> better: occurring in January or February
	# then see if those counts (or costs of them) predict any of the 
	# other event category coutns or costs
	categ = df.groupby('YEAR')['EVENT_CATEGORY'].value_counts()


	### ONE OPTION: FLoods are especially damaging, so let's look at them a
	### 			bit more.
	flood_only = df.groupby("EVENT_TYPE").get_group("Flood")
	# There are 7 categories of flood cause:
	flood_only["FLOOD_CAUSE"].value_counts()
	flood_only = flood_only[ pd.notnull( flood_only['FLOOD_CAUSE'])]
	flood_only = functions.qual_columns( flood_only, "FLOOD_CAUSE" )
	# Now, the last 7 columns hold boolean information about the 
	# flood cause... so we're ready for a linear model:
	# How does property damage, crop damage, death, and injury
	# vary with flood cause?
	flood_causes = flood_only["FLOOD_CAUSE"].value_counts().index[0:6]
	# (There are 7 causes, so regression on 6 variables)
	X = flood_only[flood_causes]	
	X = sm.add_constant(X)  # statsmodel must add constant manually
	y = flood_only["DAMAGE_PROPERTY"]
	est = sm.OLS(y,X).fit()
	mod_file = open("Flood_causes_lin_damage.txt", "w")
	mod_file.write("Multiple Linear Regression for Flood Causes: Property Damage \n")
	mod_file.write(est.summary().as_csv())
	mod_file.close()
	# R^2 coefficient is only 0.006-- weak correlation!
	# try with Deaths or Injury:
	y = flood_only["INJURIES_DIRECT"]
	est = sm.OLS(y,X).fit()
	mod_file = open("Flood_causes_lin_dinjuries.txt", "w")
	mod_file.write("Multiple Linear Regression for Flood Causes: Direct Injuries \n")
	mod_file.write(est.summary().as_csv())
	mod_file.close()
	
	y = flood_only["DEATHS_DIRECT"]
	est = sm.OLS(y,X).fit()
	mod_file = open("Flood_causes_lin_ddeaths.txt", "w")
	mod_file.write("Multiple Linear Regression for Flood Causes: Direct Deaths \n")
	mod_file.write(est.summary().as_csv())
	mod_file.close()


	# TWO: Tornadoes, by the same method. Look at Fujita scale strength
	tornado_only = df.groupby("EVENT_TYPE").get_group("Tornado")
	# 2.a:  First, treat the Fujita and Enhanced Fujita scales as though they 
	# are the same.  Both are roughly linear in wind speed categorization, 
	# wo treat Fujita rating as integer bins.
	tornado_only["TOR_F_SCALE"].value_counts()
	tornado_only = tornado_only[ pd.notnull( tornado_only['TOR_F_SCALE'])]
	tornado_only["COMBINED_FUJITA"] = tornado_only["TOR_F_SCALE"].\
					apply(functions.fujita_concat)
	# drop unknown fujita value: EFU.
	tornado_known = tornado_only[ tornado_only.COMBINED_FUJITA != -1 ]
	# simple linear regression will be a decent model here.
	functions.tornado_lin_model( tornado_known, 'COMBINED_FUJITA', \
				'DAMAGE_PROPERTY', 'cF_damage_lin.txt', 'cF_damage_plt.pdf')
	functions.tornado_lin_model( tornado_known, 'COMBINED_FUJITA', \
				'INJURIES_DIRECT', 'cF_injuries_lin.txt', 'cF_injuries_plt.pdf')
	functions.tornado_lin_model( tornado_known, 'COMBINED_FUJITA', \
				'DEATHS_DIRECT', 'cF_deaths_lin.txt', 'cF_deaths_plt.pdf')


	# Now, split Tornado data into Fujita scale vs Enhanced Fujita:
	f_only = tornado_known[ tornado_known['TOR_F_SCALE'].\
					apply(functions.Is_it_old_F)]
	ef_only = tornado_known[ tornado_known['TOR_F_SCALE'].\
					apply(functions.Is_it_old_F) == False]


	functions.tornado_lin_model( f_only, 'COMBINED_FUJITA', \
				'DAMAGE_PROPERTY', 'oldF_damage_lin.txt', 'oldF_damage_plt.pdf')
	functions.tornado_lin_model( f_only, 'COMBINED_FUJITA', \
				'INJURIES_DIRECT', 'oldF_injuries_lin.txt', 'oldF_injuries_plt.pdf')
	functions.tornado_lin_model( f_only, 'COMBINED_FUJITA', \
				'DEATHS_DIRECT', 'oldF_deaths_lin.txt', 'oldF_deaths_plt.pdf')


	functions.tornado_lin_model( ef_only, 'COMBINED_FUJITA', \
				'DAMAGE_PROPERTY', 'newF_damage_lin.txt', 'newF_damage_plt.pdf')
	functions.tornado_lin_model( ef_only, 'COMBINED_FUJITA', \
				'INJURIES_DIRECT', 'newF_injuries_lin.txt', 'newF_injuries_plt.pdf')
	functions.tornado_lin_model( ef_only, 'COMBINED_FUJITA', \
				'DEATHS_DIRECT', 'newF_deaths_lin.txt', 'newF_deaths_plt.pdf')



if __name__ == "__main__":
	main()



