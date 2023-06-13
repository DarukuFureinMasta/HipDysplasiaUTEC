# HipDysplasiaUTEC

## Project Description:
Aim of this project promoted by Universidad de Ingeniería y Tecnología (UTEC) is to develop an Xsens-DOT-IMU-based motion capture system to collect patient's 
raw biomechanical data for rehabilitation. This repository contains several Python scripts that carry out the necessary tasks for the development of the 
MoCap system:

### XSensPython/python/:
**"XSensDOT_connect_trial.py":** Script based on Xsens MVN System Development Toolkit that connects sensors to PC via Bluetooth and streams data 
in quaternions in real time. Data is also recorded in a CSV file.\
\
**"csv2sto.py":** Formats outputted CSV files into STO files so data can be read by OpenSim. Folder contains CSV example files.
               
### XSensVR/XSensPythonVR/:
**"MoBuXSens.py":** Streams quaternions in real time into Motion Builder.
