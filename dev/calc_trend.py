import pandas as pd
import matplotlib.pyplot as plt
from tools_scrape_polls import *

method_interpolate = 'linear'

# remove box around legend
plt.rcParams['legend.frameon'] = False


# import df_data.csv
df_data = pd.read_csv('./dev/df_data.csv')

# convert Date to datetime (got lost when exporting to csv)
df_data['Date'] = pd.to_datetime(df_data['Date'])


names_candidates = [col for col in df_data.columns if col not in ['Date', 'Pollster', 'Sample', 'Others']]

#df_trends = calculate_trends(df_data,names_candidates)

# resample df_data to daily frequency taking the mean over days
df_data_resampled = df_data.set_index('Date').resample('D').mean()

# drop Sample from df_data_resampled as it is not needed for the trend calculations
df_data_resampled = df_data_resampled.drop(columns=['Sample'])

if method_interpolate == 'linear':
    df_data_interpolated = df_data_resampled.interpolate(method='linear', limit_direction='both')
elif method_interpolate == 'pad':
    df_data_interpolated = df_data_resampled.interpolate(method='pad')
else:
    #logging.error('method_interpolate must be either linear or pad')
    raise ValueError('method_interpolate must be either linear or pad')

# calculate rolling average on index
df_trends = df_data_interpolated.rolling(window='7D').mean()

df_trends.head()

# overwrite trend of Others with 1 - sum of trends of all candidates  
df_trends['Others'] = 1 - df_trends.loc[:, names_candidates].sum(axis=1, skipna=False)



for col in df_data.columns[7:]:
    fig, ax = plt.subplots()
    ax.scatter(df_data['Date'], df_data[col],
            marker='o', s = 12, alpha = 0.5, color = 'blue', label = "original data")
    ax.scatter(df_data_resampled.index, df_data_resampled[col], marker='x', s = 12, alpha = 0.5, color = 'blue', label = "resampled")
    ax.plot(df_data_interpolated.index, df_data_interpolated[col], color = 'blue',
            label = 'interpolated', linestyle = 'dotted', linewidth=2)
    ax.plot(df_trends.index, df_trends[col], color = 'black',
            label = 'trend', linestyle = 'solid', linewidth=2)
    ax.plot(df_trends2.index, df_trends2[col], color = 'red',
            label = 'trend_residual', linestyle = 'solid', linewidth=2)
    ax.legend(loc='best')
    ax.set_title(col)

plot_trends_polls(df_trends, df_data, names_candidates)

