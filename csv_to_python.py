# import necessary libraries
import pandas as pd
import os
import glob

# use glob to get all the csv files
# in the folder
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))

df_fusion = pd.DataFrame()

# loop over the list of csv files
for f in csv_files:
    # read the csv file
    df = pd.read_csv(f)
    # drop the unnecessary columns
    df = df.drop(df.columns[[0, 1, 6, 7, 8, 9]], axis=1)

    # Add 'index' column to both DataFrames
    df['index'] = df.index

    # Initialize temp DataFrame with index column
    temp = pd.DataFrame()
    temp['index'] = df.index

    # Merge temp and df DataFrames on 'index' column
    temp = pd.merge(temp, df, on='index', how='outer')

    # Check if df_fusion is empty and if so, set it to temp
    if df_fusion.empty:
        df_fusion = temp
    else:
        # Merge df_fusion and temp DataFrames
        df_fusion = pd.merge(df_fusion, temp, on='index', how='outer')

# Remove the 'index' column if not needed
df_fusion = df_fusion.drop('index', axis=1)

# Prepare the header string
header = "Coordinates\nnRows={}\nnColumns={}\nendheader\n".format(df_fusion.shape[0], df_fusion.shape[1])

# Write the header to the output file
with open('output.txt', 'w') as f:
    f.write(header)

# Append the DataFrame content to the output file
df_fusion.to_csv('output.txt', sep='\t', index=False, mode='a')