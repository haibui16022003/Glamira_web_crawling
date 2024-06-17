import pandas as pd

df = pd.read_csv('image_data.csv')
print(df.shape[0])

new_df = df.drop_duplicates(df)
print(new_df.shape[0])
