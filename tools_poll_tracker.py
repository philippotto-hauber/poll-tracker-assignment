import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging

def scrape_table_and_footnotes(url = 'https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html'):
    """Scrape html table and footnotes

    Parameters:
    url (str) : url of website containing polling data

    Returns:
    df_rawdata (DataFrame) : contains content of html table as strings
    footnotes (dict)      : dict of footnotes (keys = markers, value = footnote text)  
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # table with poll data
    table = soup.find("table")

    # table headers
    names_cols = [col.text.strip() for col in table.find_all("th")]
    
    # loop over all the rows in the table and store in df
    rawdata = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        rawdata.append({names_cols[i]: cells[i].text.strip() for i in range(len(names_cols))})
    df_rawdata = pd.DataFrame(rawdata)

    # footnotes as a dict
    tmp = soup.find('ul', id='notes').find_all("li")
    footnotes = {}
    for li in tmp:
        footnotes[li['data-mark']] = li.text.replace('\n', ' ').strip()
    
    return df_rawdata, footnotes

def parse_data(df_rawdata, names_candidates_and_others, footnotes, lims_sum_shares = [0.985, 1.015]):
    """Parse poll results from html table

    Parameters:
    df_rawdata (DataFrame) : content of html table formatted as strings
    names_candidates_and_others (list): List of candidates in the election, incl. 'Others'
    footnotes (list)       : footnotes to be removed
    lims_sum_shares (list) : lower and upper limit for sum of vote shares to determine if poll should be removed

    Returns:
    df_polls (DataFrame)   : contains date of poll, pollster, sample size, vote shares in different formats (e.g. datetime, floats)
    """
    
    df_polls = df_rawdata.copy()

    # remove footnotes
    for f in footnotes.keys():
        for col in df_polls.columns:
            # according to docu default is False, but without explicitly setting it to False encountered regex error!
            df_polls[col] = df_polls[col].str.replace(f, '', regex=False) 

    # convert string columns to appropriate types
    df_polls['Date'] = pd.to_datetime(df_polls['Date'])

    df_polls['Sample'] = pd.to_numeric(df_polls['Sample'].str.replace(',', '')).astype('Int64') # replacing , if possible; float to int

    pat = re.compile(r"[0-9\.,]+")

    for col in df_polls.columns:
        if col in names_candidates_and_others:
            # convert vote shares to numeric, removing any non-numeric characters except ',' or '.
            df_polls[col] = pd.to_numeric(df_polls[col].str.findall(pat).str.join(''), errors = 'coerce') / 100.0

    # remove polls that could not be parsed 
    all_na = df_polls.loc[:, names_candidates_and_others].isna().all(axis=1)
    if sum(all_na) > 0:
        logging.warning('Excluded {} poll(s) because vote shares could not be converted to floats'.format(all_na.sum()))
    df_polls = df_polls.loc[~all_na, :]

    # remove polls whose vote shares differs from 1 by more than a given margin
    sum_shares = df_polls.loc[:, names_candidates_and_others].sum(axis=1)
    drop_row = (sum_shares < lims_sum_shares[0]) | (sum_shares > lims_sum_shares[1])
    if sum(drop_row) > 0:
        logging.warning('Excluded {} poll(s) because the sum of vote shares was smaller (larger) than {} ({}).'.format(drop_row.sum(), lims_sum_shares[0], lims_sum_shares[1]))
    df_polls = df_polls.loc[~drop_row, :]

    return df_polls

def calculate_trends(df_polls, 
                     names_candidates, 
                     k_days = '7D', 
                     method_interpolate = 'linear'):
    """Calculate trend vote shares based on poll results

    Parameters:
    df_polls (DataFrame)     : contains poll results
    names_candidates (list) : List of candidates in the election
    k_days (str)            : rolling average window in days
    method_interpolate (str): method for interpolation of missing values

    Returns:
    df_trends (DataFrame)   : contains trend vote shares (columns) over time (rows)

   """
    # resample df_polls to daily frequency taking the mean over days
    df_trends = df_polls.set_index('Date').resample('D').mean()

    # 'Sample' is not needed for the trend calculations
    df_trends = df_trends.drop(columns=['Sample'])

    # interpolate missing values
    if method_interpolate == 'linear':
        df_trends = df_trends.interpolate(method='linear', limit_direction='both')
    else:
        raise ValueError('method_interpolate must be linear')
    
    # calculate k_days rolling average
    df_trends = df_trends.rolling(window=k_days, on = df_trends.index).mean()

    # overwrite trend of Others with 1 - sum of trends of all candidates (if Others is in df_trends)
    if 'Others' in df_trends.columns:
        df_trends['Others'] = 1 - df_trends.loc[:, names_candidates].sum(axis=1, skipna=False)

    return df_trends

def export_dfs_to_csv(df_polls, df_trends):
    """Export dataframes to csv"""

    # bring columns in line with the example files
    df_polls = df_polls.rename(columns={'Date': 'date', 'Pollster': 'pollster', 'Sample': 'n'})
    df_trends.index.name = 'date'

    # write to csv
    df_polls.to_csv('./polls.csv', index=False)
    df_trends.to_csv('./trends.csv', index=True) # date is index!

