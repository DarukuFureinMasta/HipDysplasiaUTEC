import socket
import pyfbsdk_init
import pyfbsdk

from pyfbsdk import FBApplication, FBSystem, FBFindModelByLabelName, FBBodyNodeId, FBTime, FBTake

# Create a new server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12345  # change to your port
sock.bind(('localhost', port))
sock.listen(1)

# Get the system
system = pyfbsdk.FBSystem()

# Get the model (the joint you want to control)
# Replace 'WristJoint' with the actual name of your joint
model = FBFindModelByLabelName('WristJoint')


while True:
    print("Waiting for a connection...")
    connection, client_address = sock.accept()

    try:
        print("Connection from", client_address)

        # Receive the data in small chunks
        while True:
            data = connection.recv(16)
            if data:
                # Assuming you are receiving quaternion as w,x,y,z floats
                q = list(map(float, data.decode('utf-8').split(',')))

                # Make sure we have exactly 4 values
                if len(q) != 4:
                    print("Invalid data received")
                    break

                # Apply the quaternion to the joint rotation
                model.Rotation = pyfbsdk.FBRVector(q[0], q[1], q[2], q[3])
            else:
                break
    finally:
        # Clean up the connection
        connection.close()