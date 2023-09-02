#%% load packages
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tools_scrape_polls import *

#%% set up logging
logging.basicConfig(filename = "scrape_polls.log", 
                    level = logging.INFO,
                    format = '%(levelname)s: %(asctime)s %(message)s',
                    filemode = 'w')

#%% load table from website
url = 'https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html'

table = scrape_table(url)
footnotes = ['*', '**']

name_cols = [col.text.strip() for col in table.find_all("th")]
n_col = len(name_cols)
n_row = table.find_all("tr")
names_candidates = [col for col in name_cols if col not in ['Date', 'Pollster', 'Sample', 'Others']]
n_candidates = len(names_candidates)
names_candidates_and_others = [col for col in name_cols if col not in ['Date', 'Pollster', 'Sample']]

#%% parse data
 
# loop over all the rows in the table and store data in df
rawdata = []
for row in table.find_all("tr"):
    cells = row.find_all("td")
    rawdata.append({name_cols[i]: cells[i].text.strip() for i in range(len(name_cols))})

df_rawdata = pd.DataFrame(rawdata)

# remove footnotes
for f in footnotes:
    df_rawdata.replace(f, '')

# convert columns from strings to appropriate types
df_data = df_rawdata.copy()
df_data['Date'] = pd.to_datetime(df_data['Date'])

df_data['Sample'] = pd.to_numeric(df_data['Sample'].str.replace(',', ''), errors='coerce').astype('Int64') # replacing , if possible; float to int

for col in df_data.columns:
    if col not in ['Date', 'Sample', 'Pollster']:
        # removing % when needed and dividing by 100.0
        df_data[col] = pd.to_numeric(df_data[col].str.replace('%', ''), errors='coerce') / 100.0


# check if shares sum to 1
drop_row = (df_data.loc[:, names_candidates_and_others].sum(axis=1, skipna=False) > 1.01) | (df_data.loc[:, names_candidates_and_others].sum(axis=1, skipna=False) < 0.99)

df_data_excluded = df_data.loc[drop_row, :] # only for dev purposes
df_data = df_data.loc[~drop_row, :]
logging.warning('Excluded {} rows because of possible data entry errors: sum of vote shares larger (smaller) than 1.01 (0.99).'.format(drop_row.sum()))

df_data.head()
df_data.dtypes
df_data.info(show_counts=True)

#%% calculate trends
df_trends = calculate_trends(df_data, 
                             names_candidates,
                             k_days= '7D',
                             method_interpolate='linear')

# %% plot trends (only for dev purposes)

plot_trends_polls(df_trends, df_data, names_candidates)

#%% export to csv

# rename columns to bring in line with the example files
df_data = df_data.rename(columns={'Date': 'date', 'Pollster': 'pollster', 'Sample': 'n'})
df_trends.index.name = 'date'

# write to csv
df_data.to_csv('polls.csv', index=False)
df_trends.to_csv('trends.csv', index=True) # date is index!

#%% To-Dos

# ~~backward moving average~~
# read in footnotes from website -> id_notes etc.
# check which polls could not be parsed
# check if shares sum to 1
# check if outliers are present -> Bulstrode mid November
# add logging
# move functions like loading data, calculating trends etc. to separate file


# rename index of df_trends to date
# 

