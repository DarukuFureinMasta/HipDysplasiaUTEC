import os
os.add_dll_directory("C:/OpenSim4.4/bin")
import opensim

# Specify the path to the OSIM file
model_file = "FullBodyModel-4.0 (1)\FullBodyModel-4.0\Rajagopal2015.osim"

# Load the model from the OSIM file
model = opensim.Model(model_file)

# Print some information about the loaded model
print("Model name: {}".format(model.getName()))
print("Number of bodies: {}".format(model.getNumBodies()))
print("Number of degrees of freedom: {}".format(model.getNumCoordinates()))