import pandas as pd

data1 = pd.read_csv('online_presence_dashboard/data/raw/mz,dlp,ast,xtra,alpha.csv')
data2 = pd.read_csv('online_presence_dashboard/data/raw/novis,keep,patient,indep.csv')
home_data=pd.read_csv('online_presence_dashboard/data/raw/hms-rpf,dwel,lpm,hiline.csv')
extra = pd.read_csv('online_presence_dashboard/data/raw/aus_med_supplies.csv')
print(data1.head())
print(data2.head())
print(home_data.head())

merged_df = data1.merge(data2, on='Date').merge(home_data, on='Date')
merged_df = merged_df.merge(extra, on='Date')
merged_df = merged_df.rename(columns={'Visits': 'ausmedsupply.com.au'})
merged_df.to_csv('data/processed/traffic.csv', index=False)
print(merged_df)