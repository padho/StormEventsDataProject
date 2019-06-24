import sys
import glob
import math
import sqlalchemy
import pandas as pd

import functions


# psql_username = sys.argv[1]
# psql_password = sys.argv[2]
psql_localhost = "127.0.0.1"
psql_database = "storms"


def LoadFile( ):
    path = r'details/test/' #r'details/1996-2018/'
    allFiles = glob.glob(path + "*.csv")
    df = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
    	frame = pd.read_csv(file_, index_col=None, \
    			    header = 0, low_memory = False)
    	list_.append(frame)
    df = pd.concat(list_)
    return df

def clean_details(df):

    # Remove endlines from test columns
    df = df.replace(r'\\n',' ', regex=True)

    # Convert DAMAGE_PROPERTY and DAMAGE_CROPS columns to real float values
    df['DAMAGE_PROPERTY'] = df['DAMAGE_PROPERTY'].apply(functions.convert_num)
    df['DAMAGE_PROPERTY'] = df['DAMAGE_PROPERTY'].fillna(0)
    df['DAMAGE_CROPS'] = df['DAMAGE_CROPS'].apply(functions.convert_num)
    df['DAMAGE_CROPS'] = df['DAMAGE_CROPS'].fillna(0)

    # Collect similar events together
    df["EVENT_CATEGORY"] = df["EVENT_TYPE"].apply(functions.collect_events)

    # remove white spaces from column names:
    df.columns = df.columns.str.replace(' ', '')

    return df

def main():

    psql_username = sys.argv[1]
    psql_password = sys.argv[2]
    # Connect to database.  no table has been created yet
    connection = "postgresql://"+psql_username+":"+psql_password+"@" \
              + psql_localhost +'/' + psql_database
    engine = sqlalchemy.create_engine(connection)
    con = engine.connect()

    print("The database should be schema only at this stage:")
    print(engine.table_names())
    
    # Get file list for storm events details table, 1996-2018	
    path =  r'details/1996-2018/'
    allFiles = glob.glob(path+ "*.csv")
    table_name = 'event_details'

    # For each file, read .csv file into a dataframe, clean variables, then
    # upload into psql database
    for file_ in allFiles:
        df = pd.read_csv(file_, index_col=None, \
                         header = 0, low_memory = False)

        df = df.replace(r'\\n',' ', regex=True)
        df = clean_details(df) 
        df.columns = map(str.lower, df.columns)
        # Now store storm details in table:
        df.to_sql(name=table_name, con=connection, if_exists='append', index=False)

    print(engine.table_names())
    con.close()


if __name__ == "__main__":
	main()



