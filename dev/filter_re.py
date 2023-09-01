
import pandas as pd
import re

df_data = pd.read_csv('./dev/df_data_pre_parsing.csv')

df_data.dtypes

col = 'Bulstrode'
pat = re.compile(r"[0-9\.,]+")
tmp = df_data[col].str.findall(pat).str.join('')
tmp_numeric = pd.to_numeric(tmp)



