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

#%% parse data

pat = re.compile(r"[0-9\.,]+")

for col in df_data.columns:
    if col not in ['Date', 'Sample', 'Pollster']:
        # removing % when needed and dividing by 100.0
        df_data[col] = pd.to_numeric(df_data[col].str.findall(pat).str.join('')) / 100.0

df_data.dtypes

#%% find polls that could not be parsed

all_na = df_data.loc[:, names_candidates_and_others].isna().all(axis=1)

polls_not_parsed = df_data.loc[all_na, :]

polls_not_parsed.head()

# %% find possible data entry errors

lim_upr = 1.02
lim_lwr = 0.98
sum_shares = df_data.loc[:, names_candidates_and_others].sum(axis=1)
drop_row = (sum_shares> lim_upr) | (sum_shares < lim_lwr)

df_data_excluded = df_data.loc[drop_row, :] # only for dev purposes
df_data_2 = df_data.loc[~drop_row, :]

df_data.loc[137, names_candidates_and_others].sum()
#logging.warning('Excluded {} rows because of possible data entry errors: sum of vote shares larger (smaller) than 1.01 (0.99).'.format(drop_row.sum()))

# %%
