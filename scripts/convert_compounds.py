import pyreadr
import pandas as pd

# Let's inspect the files
try:
    c_final = pyreadr.read_r('data/TCMNP/data/compoundfinal.rda')
    df = c_final[list(c_final.keys())[0]]
    print("compoundfinal.rda columns:", df.columns.tolist())
    print(df.head())
except Exception as e: print(e)

try:
    c_data = pyreadr.read_r('data/TCMNP/data/compound_data.rda')
    df2 = c_data[list(c_data.keys())[0]]
    print("compound_data.rda columns:", df2.columns.tolist())
    print(df2.head())
except Exception as e: print(e)
