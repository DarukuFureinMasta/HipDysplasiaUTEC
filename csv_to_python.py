# import necessary libraries
import pandas as pd
import os
import glob

# use glob to get all the csv files
# in the folder
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))

index = [x/100 for x in range(0, 614)]


df_fusion = pd.DataFrame()

list1 = ["antebrazo", "hombro", "muneca"]
df_fusion["time"] = index
i=0
# loop over the list of csv files
for f in csv_files:
    # read the csv file
    df = pd.read_csv(f)
    # drop the unnecessary columns
    df = df.drop(df.columns[[0, 1, 6, 7, 8, 9]], axis=1)

    # Add 'index' column to both DataFrames
    # Initialize temp DataFrame with index column
    temp = pd.DataFrame()
    df['Quat_W'] = df['Quat_W'].astype(str)
    df['Quat_X'] = df['Quat_X'].astype(str)
    df['Quat_Y'] = df['Quat_Y'].astype(str)
    df['Quat_Z'] = df['Quat_Z'].astype(str)
    temp[list1[i]] = df[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].apply(lambda x: ','.join(x), axis=1)
    i+=1
    if df_fusion.empty:
        df_fusion = temp
    else:
        # Merge df_fusion and temp DataFrames
        df_fusion = pd.concat([df_fusion, temp], axis=1)

# Remove the 'index' column if not needed
# df_fusion = df_fusion.drop('index', axis=1)

# Prepare the header string
header = "Coordinates\nnRows={}\nnColumns={}\nendheader\n".format(df_fusion.shape[0], df_fusion.shape[1])

# Write the header to the output file
with open('output.txt', 'w') as f:
    f.write(header)

# Append the DataFrame content to the output file
df_fusion.to_csv('output.txt', sep='\t', index=False, mode='a')