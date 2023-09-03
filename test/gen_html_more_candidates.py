import pandas as pd

# read in df_polls
df_polls = pd.read_csv('./../polls.csv')

# drop column Others
#df_polls = df_polls.drop(columns=['Others'])

new_candidates = ['Brown', 'Mouse']

# add columns for new candidates in df_polls
for candidate in new_candidates:
    df_polls[candidate] = 0

candidates = [col for col in df_polls.columns if col not in ['date', 'pollster', 'n']]
# generate random simplex
import numpy as np
np.random.seed(42)
df_polls.loc[:, candidates] = np.random.dirichlet(np.ones(len(candidates)), size=len(df_polls))

# rename columns in df_polls date - Date, pollster - Pollster, n -> Sample
df_polls = df_polls.rename(columns={'date': 'Date', 'pollster': 'Pollster', 'n': 'Sample'})

df_polls.to_html('./more_candidates.html', index=False)