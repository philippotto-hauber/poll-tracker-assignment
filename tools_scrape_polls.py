import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
import logging
sns.set_style("darkgrid")

# function to scrape table from url
def scrape_table(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    return table

def parse_data(table, name_cols, names_candidates_and_others, footnotes, lims_sum_shares = [0.98, 1.02]):
    # loop over all the rows in the table and store in df
    rawdata = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        rawdata.append({name_cols[i]: cells[i].text.strip() for i in range(len(name_cols))})
    df_rawdata = pd.DataFrame(rawdata)
    df_data = df_rawdata.copy()

    # remove footnotes
    for f in footnotes:
        df_data.replace(f, '')

    # convert string columns to appropriate types
    df_data['Date'] = pd.to_datetime(df_data['Date'])

    df_data['Sample'] = pd.to_numeric(df_data['Sample'].str.replace(',', ''), errors='coerce').astype('Int64') # replacing , if possible; float to int

    pat = re.compile(r"[0-9\.,]+")

    for col in df_data.columns:
        if col not in ['Date', 'Sample', 'Pollster']:
            # convert vote shares to numeric, removing any non-numeric characters except ',' or '.
            df_data[col] = pd.to_numeric(df_data[col].str.findall(pat).str.join('')) / 100.0

    # remove polls that could not be parsed 
    all_na = df_data.loc[:, names_candidates_and_others].isna().all(axis=1)
    df_polls_not_parsed = df_data.loc[all_na, :]
    if sum(all_na) > 0:
        print('Excluded {} row(s) because vote shares could not be converted to floats'.format(all_na.sum()))
    df_data = df_data.loc[~all_na, :]

    # remove polls whose vote shares differs from 1 by more than a given margin
    sum_shares = df_data.loc[:, names_candidates_and_others].sum(axis=1)
    drop_row = (sum_shares < lims_sum_shares[0]) | (sum_shares > lims_sum_shares[1])
    df_data_excluded = df_data.loc[drop_row, :] 
    if sum(drop_row) > 0:
        print('Excluded {} row(s) because the sum of vote shares was smaller (larger) than {} ({}).'.format(drop_row.sum(), lims_sum_shares[0], lims_sum_shares[1]))
    df_data = df_data.loc[~drop_row, :]

    return df_data


# function to calculate trend
def calculate_trends(df_data, 
                     names_candidates, 
                     k_days = '7D', 
                     method_interpolate = 'linear'):
    """Calculate trend vote shares based on poll results

    Parameters:
    df_data (DataFrame)     : contains poll results
    names_candidates (list) : List of candidates in the election
    k_days (str)            : rolling average window in days
    method_interpolate (str): method for interpolation of missing values

    Returns:
    df_trends (DataFrame)   : contains trend vote shares (columns) over time (rows)

   """
    # resample df_data to daily frequency taking the mean over days
    df_trends = df_data.set_index('Date').resample('D').mean()

    # 'Sample' is not needed for the trend calculations
    df_trends = df_trends.drop(columns=['Sample'])

    # interpolate missing values
    if method_interpolate == 'linear':
        df_trends = df_trends.interpolate(method='linear', limit_direction='both')
    elif method_interpolate == 'pad':
        df_trends = df_trends.interpolate(method='pad')
    else:
        logging.error('method_interpolate must be either linear or pad')
        #raise ValueError('method_interpolate must be either linear or pad')
    
    # calculate k_days rolling average
    df_trends = df_trends.rolling(window=k_days, on = df_trends.index).mean()

    # overwrite trend of Others with 1 - sum of trends of all candidates
    df_trends['Others'] = 1 - df_trends.loc[:, names_candidates].sum(axis=1, skipna=False)

    return df_trends

# function to plot trends and polls -> only for dev purposes
def plot_trends_polls(df_trends, df_data, names_candidates, ylim = [-0.05, 0.6]):
    fig, ax = plt.subplots()
    colors_plot = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    counter_colors = 0
    for col in df_trends.columns:
        if col in names_candidates:
            ax.plot(df_trends.index, df_trends[col], color = colors_plot[counter_colors],
                    label = col, linestyle = 'solid', linewidth=2)
            ax.scatter(df_data['Date'], df_data[col], 
                    marker='o', s = 12, alpha = 0.5, color = colors_plot[counter_colors])
            counter_colors += 1

    ax.legend(loc='best', ncol=2, fontsize=10, frameon=False)
    ax.set_ylim(ylim)
    ax.set_title('Vote shares and trends')
    fig.savefig('plot_trends.png', dpi=300)