import pyreadr
import pandas as pd

result = pyreadr.read_r('data/TCMNP/data/herb_pm.rda')
df = result['herb_pm']
df.to_csv('data/herb_pm.csv', index=False)
print(df.head())
print(df.columns.tolist())
