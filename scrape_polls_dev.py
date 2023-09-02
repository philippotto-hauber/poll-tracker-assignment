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

df_data = parse_data(table, 
                    name_cols, 
                    names_candidates_and_others, 
                    footnotes, 
                    lims_sum_shares = [0.98, 1.02])

# df_data.head()
# df_data.dtypes
# df_data.info(show_counts=True)

#%% calculate trends
df_trends = calculate_trends(df_data, 
                             names_candidates,
                             k_days= '7D',
                             method_interpolate='linear')

# %% plot trends (only for dev purposes)

plot_trends_polls(df_trends, df_data, names_candidates)

#%% export to csv

export_dfs_to_csv(df_data, df_trends)
# # rename columns to bring in line with the example files
# df_data = df_data.rename(columns={'Date': 'date', 'Pollster': 'pollster', 'Sample': 'n'})
# df_trends.index.name = 'date'

# # # write to csv
# df_data.to_csv('polls.csv', index=False)
# df_trends.to_csv('trends.csv', index=True) # date is index!

#%% To-Dos

# read in footnotes from website -> id_notes etc.


# 

