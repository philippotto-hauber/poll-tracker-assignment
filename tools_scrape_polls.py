import requests
from bs4 import BeautifulSoup
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

# function to calculate trend
def calculate_trends(df_data, names_candidates, k_days = '7D', method_interpolate = 'linear'):
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
    df_trends = df_data.set_index('Date').resample('D').mean().reset_index()

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
    df_trends = df_trends.rolling(window=k_days).mean()

    # overwrite trend of Others with 1 - sum of trends of all candidates
    df_trends['Others'] = 1 - df_trends.loc[:, names_candidates].sum(axis=1, skipna=False)


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