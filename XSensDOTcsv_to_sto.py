# import necessary libraries
import pandas as pd
import os
import glob

# use glob to get all the csv files
# in the folder
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))

#Variables
DataRate = 60.00 #Has to be a float
FileName = 'XSensDOTOutput'


index = [x/DataRate for x in range(0, 614)] # 100 changed to 60#

df_fusion = pd.DataFrame()

list1 = ["humerus_r_imu", "torso_imu", "radius_r_imu"]# Sensor name      #Base IMU will be the second one
df_fusion["time"] = index
i=0
# loop over the list of csv files
for f in csv_files:
    # read the csv file
    df = pd.read_csv(f)
    # drop the unnecessary columns 
    df = df.drop(df.columns[[0, 1, 6, 7, 8, 9]], axis=1) # Formated for CSV sensor output

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

# Prepare the header string
header = "DataRate={}\nDataType=Quaternion\nVersion=3\nOpenSimVersion=4.1\nendheader\n".format(DataRate,df_fusion.shape[0], df_fusion.shape[1])

# Write the header to the output file
with open('{}.sto'.format(FileName), 'w') as f:# File name
    f.write(header)

# Append the DataFrame content to the output file
df_fusion.to_csv('{}.sto'.format(FileName), sep='\t', index=False, mode='a')# File name

# Write the header to the second output file
with open('{}_calibration.sto'.format(FileName), 'w') as f:# File name
    f.write(header)

# Write the first row of data to the second output file
df_fusion.iloc[[0]].to_csv('{}_calibration.sto'.format(FileName), sep='\t', index=False, mode='a')# File name

# Write the header and all the data to the .xml file
with open('IMU_Placer_SetUp.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    f.write('<OpenSimDocument Version="44000">\n')
    f.write('\t<IMUPlacer>\n')
    f.write('\t\t<!--The label of the base IMU in the orientation_file_for_calibration used to account for the heading difference between the sensor data and the forward direction of the model. Leave blank if no heading correction is desired.-->\n')
    f.write('\t\t<base_imu_label>{}</base_imu_label>\n'.format(list1[1]))
    f.write('\t\t<!--The axis of the base IMU that corresponds to its heading direction. Options are \'x\', \'-x\', \'y\', \'-y\', \'z\' or \'-z\'. Leave blank if no heading correction is desired.-->\n')
    f.write('\t\t<base_heading_axis>z</base_heading_axis>\n')
    f.write('\t\t<!--Space fixed Euler angles (XYZ order) from IMU Space to OpenSim. Default (0, 0, 0).-->\n')
    f.write('\t\t<sensor_to_opensim_rotations>-1.5707963267948966 0 0</sensor_to_opensim_rotations>\n')
    f.write('\t\t<!--Name/path to a .sto file of sensor frame orientations as quaternions to be used for calibration.-->\n')
    f.write('\t\t<orientation_file_for_calibration>{}_calibration.sto</orientation_file_for_calibration>\n'.format(FileName))#Calibration filename
    f.write('\t</IMUPlacer>\n')
    f.write('</OpenSimDocument>')
	

   