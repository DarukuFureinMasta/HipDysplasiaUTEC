import pandas as pd
import os
import glob

path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))

#Variables
DataRate = 60.00
FileName1 = 'output'
FileName2 = 'calibration'
Frames = 614

# Initializing data frame with time as index
index = [x/DataRate for x in range(0, Frames)]
df_fusion = pd.DataFrame()
df_fusion["time"] = index

# Loop over CSV files (f) and IMUs (i)
i = 0
list1 = ["humerus_r_imu", "torso_imu", "radius_r_imu"]
for f in csv_files:

    # Storing current CSV file
    df = pd.read_csv(f)

    # Drop the unnecessary columns 
    df = df.drop(df.columns[[0, 1, 6, 7, 8, 9]], axis=1)

    # Initializing temporal data frame
    temp = pd.DataFrame()

    # Converting all columns of current data frame into string data types
    df['Quat_W'] = df['Quat_W'].astype(str)
    df['Quat_X'] = df['Quat_X'].astype(str)
    df['Quat_Y'] = df['Quat_Y'].astype(str)
    df['Quat_Z'] = df['Quat_Z'].astype(str)

    # Joining all columns of current data frame into a single column
    temp[list1[i]] = df[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].apply(lambda x: ','.join(x), axis=1)
    i += 1

    # Merging output data frame with now formatted temporal data frame
    df_fusion = pd.concat([df_fusion, temp], axis=1)

# Formatting header
header = "DataRate={}\nDataType=Quaternion\nVersion=3\nOpenSimVersion=4.1\nendheader\n".format(DataRate)

# STO output file
with open('{}.sto'.format(FileName1), 'w') as f:
    f.write(header)
df_fusion.to_csv('{}.sto'.format(FileName1), sep='\t', index=False, mode='a')

# Second STO output file (calibration)
with open('{}.sto'.format(FileName2), 'w') as f:
    f.write(header)
df_fusion.iloc[[0]].to_csv('{}.sto'.format(FileName2), sep='\t', index=False, mode='a')

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
    f.write('\t\t<orientation_file_for_calibration>{}.sto</orientation_file_for_calibration>\n'.format(FileName2)) #Calibration filename
    f.write('\t</IMUPlacer>\n')
    f.write('</OpenSimDocument>')

    # Successful creation check 
    output_path = '{}.sto'.format(FileName1)
    if os.path.exists(output_path):
        print(f"\nSuccesfully created {FileName1}.sto")
    else:
        print(f"\nError while creating {FileName1}.sto")

    output_path = '{}.sto'.format(FileName2)
    if os.path.exists(output_path):
        print(f"Succesfully created {FileName2}.sto\n")
    else:
        print(f"Error while creating {FileName2}.sto\n")