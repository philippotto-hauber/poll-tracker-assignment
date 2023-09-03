import pandas as pd

# read in df_polls
df_polls = pd.read_csv('./../polls.csv')
# reand in df_trends
df_trends = pd.read_csv('./../trends.csv')

# read in polls.example.csv
df_polls_example = pd.read_csv('./../../polls.example.csv')

# read in trends.example.csv
df_trends_example = pd.read_csv('./../../trends.example.csv')

# find dates that are in df_polls but not in df_polls_example
date_polls = df_polls['date']
date_polls_example = df_polls_example['date']
tmp = date_polls[~date_polls.isin(date_polls_example)]
print('dates in df_polls but not in df_polls_example:')
print(tmp)

tmp = date_polls_example[~date_polls_example.isin(date_polls)]
print('dates in df_polls_example but not in df_polls:')
print(tmp)


# do the same for df_trends
date_trends = df_trends['date']
date_trends_example = df_trends_example['date']
tmp = date_trends[~date_trends.isin(date_trends_example)]
print('dates in df_trends but not in df_trends_example:')
print(tmp)

tmp = date_trends_example[~date_trends_example.isin(date_trends)]
print('dates in df_trends_example but not in df_trends:')
print(tmp)

# conver date column to datetime
df_trends['date'] = pd.to_datetime(df_trends['date'])

# get a range of dates from min and max of df_trends
dates = pd.date_range(start=df_trends['date'].min(), 
              end=df_trends['date'].max(),
              freq = 'D')

# the length of this range should be equal to the number of rows if all dates are present in df_trends
len(dates) == df_trends.shape[0]

# check that the number of days for which we have polls is lower 
date_polls_unique = date_polls.unique()
len(date_polls_unique)

# but min and max coincide -> when aggregating and setting the date index empty values are inserted for those days where there are no polls 
date_polls.max() == date_trends.max()
date_polls.min() == date_trends.min()