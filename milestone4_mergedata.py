# =============================================================================
# Milestone 4: Merging dataset
# =============================================================================

import pandas as pd
import datetime as dt

# =============================================================================
# Part 1: Loading relevant datasets
# =============================================================================

#1. df comprises basic info on stocks
data = pd.ExcelFile('stock60_final.xlsx')
print(data.sheet_names)
df = data.parse('stock60')

#2. df2 comprises stock prices and volume for 3 months (obtained in milestone 3)
df2 = pd.read_csv('stocks60.csv',index_col=0)
df2['filters'] = df2.name.map(df.set_index('name')['filters'])
df2['board'] = df2.name.map(df.set_index('name')['board'])
df2['difpct'] = df2.groupby('name').close.apply(lambda x: x.pct_change()).values
df2 = df2.dropna()
df2order = df2[['filters','day','name','board', 'close', 'open', 'high', 'low', 'volume', 'dif','difpct']]
df2order['day'] = pd.to_datetime(df2order['day'])

#3. df_senti comprises the sentiment data (derived from milestone4_tweet.py)
df_senti = pd.read_csv('senti60.csv',index_col=0)
df_senti['timestamp'] = df_senti['timestamp.1'].apply(lambda x : pd.to_datetime(str(x)))
df_senti['day'] = df_senti['timestamp'].dt.date
df_senti2 = df_senti.groupby(['filters','day'])['compound'].mean().reset_index(name = 'avg_senti')
df_senti2['senticlass']=df_senti2['avg_senti'].apply(lambda x: (x>0 and 'Positive') or (x<0 and 'Negative') or 'Neutral')
df_senti2['day']  = pd.to_datetime(df_senti2['day'])

# =============================================================================
# Part 2: Merge datasets
# =============================================================================

#1st approach: merge data based on intersect values
merged_df_clean = pd.merge(df2order,df_senti2,on=['filters','day'],how='inner')
merged_df_clean['target'] = merged_df_clean['difpct'].apply(lambda x: (x>0 and 'Up') or (x<0 and 'Down') or 'Unchanged')
merged_df_clean.to_csv('mergestockclean.csv',index=False)

# 2nd approach: merge all data including nan values
merged_df_union = pd.merge(df2order,df_senti2,on=['filters','day'],how='left')
merged_df_union['target'] = merged_df_union['difpct'].apply(lambda x: (x>0 and 'Up') or (x<0 and 'Down') or 'Unchanged')
merged_df_union.to_csv('mergestock.csv',index=False)
