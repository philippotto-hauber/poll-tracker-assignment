#%% dependencies
import pandas as pd
import re



#%% load data
df_data = pd.read_csv('./dev/df_rawdata.csv')

#%% add row that cannot be parsed
df_data = df_data.append({'Date': '2020-11-01', 
                        'Pollster': 'Megalomania Inc.', 
                        'Sample': '1,000', 
                        'Bulstrode': 'thirty one',
                        'Lydgate': 'twenty nine',
                        'Vincy': 'twenty two',
                        'Casaubon': 'ten',
                        'Chettam': '',
                        'Others': 'eight'}, 
                        ignore_index=True)
#%% add row that cannot be parsed totally -> will be dropped when checking sum of shares
df_data = df_data.append({'Date': '2021-11-01', 
                        'Pollster': 'Megalomania Inc.', 
                        'Sample': '1,000', 
                        'Bulstrode': '31.9%',
                        'Lydgate': '29.2%',
                        'Vincy': '19.5%',
                        'Casaubon': 'ten point one percent',
                        'Chettam': '1.3%',
                        'Others': '8%'}, 
                        ignore_index=True)

#%% define some auxiliary vars 
names_candidates_and_others = [col for col in df_data.columns if col not in ['Date', 'Pollster', 'Sample']]

footnotes = ['*', '**']

#%% remove footnotes
for f in footnotes:
    df_data.replace(f, '')

#%% parse data

df_data['Date'] = pd.to_datetime(df_data['Date'])

df_data['Sample'] = pd.to_numeric(df_data['Sample'].str.replace(',', ''), errors='coerce').astype('Int64') # replacing , if possible; float to int

pat = re.compile(r"[0-9\.,]+")

for col in df_data.columns:
    if col not in ['Date', 'Sample', 'Pollster']:
        # convert vote shares to numeric, removing any non-numeric characters except ',' or '.
        df_data[col] = pd.to_numeric(df_data[col].str.findall(pat).str.join('')) / 100.0

df_data.dtypes

#%% find polls that could not be parsed

all_na = df_data.loc[:, names_candidates_and_others].isna().all(axis=1)

polls_not_parsed = df_data.loc[all_na, :]
print('Excluded {} row(s) because vote shares could not be converted to floats'.format(polls_not_parsed.shape[0]))
df_data = df_data.loc[~all_na, :]

# %% find possible data entry errors

lim_upr = 1.02
lim_lwr = 0.98
sum_shares = df_data.loc[:, names_candidates_and_others].sum(axis=1)
drop_row = (sum_shares> lim_upr) | (sum_shares < lim_lwr)

df_data_excluded = df_data.loc[drop_row, :] # only for dev purposes
df_data = df_data.loc[~drop_row, :]

print('Excluded {} row(s) because the sum of vote shares was larger (smaller) than {} ({}).'.format(drop_row.sum(), lim_upr, lim_lwr))

#%% check result
df_data.dtypes
df_data.info(show_counts=True)


