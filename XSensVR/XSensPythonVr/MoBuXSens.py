
#  Copyright (c) 2003-2022 Movella Technologies B.V. or subsidiaries worldwide.
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#  
#  1.	Redistributions of source code must retain the above copyright notice,
#  	this list of conditions and the following disclaimer.
#  
#  2.	Redistributions in binary form must reproduce the above copyright notice,
#  	this list of conditions and the following disclaimer in the documentation
#  	and/or other materials provided with the distribution.
#  
#  3.	Neither the names of the copyright holders nor the names of their contributors
#  	may be used to endorse or promote products derived from this software without
#  	specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
#  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
#  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  

# Requires installation of the correct Xsens DOT PC SDK wheel through pip
# For example, for Python 3.9 on Windows 64 bit run the following command
# pip install xsensdot_pc_sdk-202x.x.x-cp39-none-win_amd64.whl

import time
from pynput import keyboard
from threading import Lock
import xsensdot_pc_sdk
from user_settings import *
from collections import defaultdict
import socket
import sys

waitForConnections = True


class CallbackHandler(xsensdot_pc_sdk.XsDotCallback):
    def __init__(self, max_buffer_size=5):
        xsensdot_pc_sdk.XsDotCallback.__init__(self)
        self.m_detectedDots = list()
        self.m_errorReceived = False
        self.m_maxNumberOfPacketsInBuffer = max_buffer_size
        self.m_packetBuffer = defaultdict(list)
        self.m_lock = Lock()

    def getDetectedDots(self):
        return self.m_detectedDots

    def errorReceived(self):
        return self.m_errorReceived

    def packetsAvailable(self):
        for dev in self.m_detectedDots:
            if self.packetAvailable(dev.bluetoothAddress()) == 0:
                return False
        return True

    def packetAvailable(self, bluetoothAddress):
        self.m_lock.acquire()
        res = len(self.m_packetBuffer[bluetoothAddress]) > 0
        self.m_lock.release()
        return res

    def getNextPacket(self, bluetoothAddress):
        if len(self.m_packetBuffer[bluetoothAddress]) == 0:
            return None
        self.m_lock.acquire()
        oldest_packet = xsensdot_pc_sdk.XsDataPacket(self.m_packetBuffer[bluetoothAddress].pop(0))
        self.m_lock.release()
        return oldest_packet

    def onAdvertisementFound(self, port_info):
        if not whitelist or port_info.bluetoothAddress() in whitelist:
            self.m_detectedDots.append(port_info)
        else:
            print(f"Ignoring {port_info.bluetoothAddress()}")

    def onBatteryUpdated(self, dev, batteryLevel, chargingStatus):
        print(dev.deviceTagName() + f" BatteryLevel: {batteryLevel} Charging status: {chargingStatus}")

    def onError(self, errorString):
        print(f"Error received: {errorString}")
        self.m_errorReceived = True

    def onLiveDataAvailable(self, dev, pack):
        self.m_lock.acquire()
        while len(self.m_packetBuffer[dev.portInfo().bluetoothAddress()]) >= self.m_maxNumberOfPacketsInBuffer:
            self.m_packetBuffer[dev.portInfo().bluetoothAddress()].pop()
        self.m_packetBuffer[dev.portInfo().bluetoothAddress()].append(xsensdot_pc_sdk.XsDataPacket(pack))
        self.m_lock.release()

def on_press(key):
    global waitForConnections
    waitForConnections = False

# Setup the client socket
def setup_socket():
    # Create a socket object
    socket1 = socket.socket()
    # Define the port on which you want to connect
    port = 12345
    # Connect to the server on local computer
    socket1.connect(('127.0.0.1', port))
    return socket1

# Sensor Connection Trial and Retrial
def ConnectionAttempts():
    #Number of connection retrials
    retry_number=7
    for attempt in range(retry_number):
        print(f"Attempt {attempt+1} @ {address}")
        if manager.openPort(portInfo):
            print(f'Succesful Connection {address} ')
            return 0
        else:
            print(f"Connection to Device {address} failed, retrying...")
            print (f"Retrying connection to {address}")
            continue
    return 1



if __name__ == "__main__":
    # Setting up the socket
    socket1 = setup_socket()

    # Print SDK version
    version = xsensdot_pc_sdk.XsVersion()
    xsensdot_pc_sdk.xsdotsdkDllVersion(version)
    print(f"Using Xsens DOT SDK version: {version.toXsString()}")

    # Create connection manager
    manager = xsensdot_pc_sdk.XsDotConnectionManager()
    if manager is None:
        print("Manager could not be constructed, exiting.")
        exit(-1)

    # Create and attach callback handler to connection manager
    callback = CallbackHandler()
    manager.addXsDotCallbackHandler(callback)

    # Start a scan and wait until we have found one or more DOT Devices
    print("Scanning for devices...")
    manager.enableDeviceDetection()

    # Setup the keyboard input listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print("Press any key or wait 20 seconds to stop scanning...")
    connectedDOTCount = 0
    startTime = xsensdot_pc_sdk.XsTimeStamp_nowMs()

    while waitForConnections and not callback.errorReceived() and xsensdot_pc_sdk.XsTimeStamp_nowMs() - startTime <= 20000:
        time.sleep(0.1)

        nextCount = len(callback.getDetectedDots())
        if nextCount != connectedDOTCount:
            print(f"Number of connected DOTs: {nextCount}. Press any key to start.")
            connectedDOTCount = nextCount

    manager.disableDeviceDetection()
    print("Stopped scanning for devices.")

    if len(callback.getDetectedDots()) == 0:
        print("No Xsens DOT device(s) found. Aborting.")
        exit(-1)

    # Set the device tag name of a device

    deviceList = list()
    for portInfo in callback.getDetectedDots():
        address = portInfo.bluetoothAddress()
        if ConnectionAttempts() == 1:
            user_input=input("Do you want to continue triying (1), follow along (2) or abort (3)")
            if user_input ==1:
                print("Retrying")
                continue
            elif user_input == 2:
                print("Following along")
                print(f"Giving up {address} :( Reason: {manager.lastResultText()}")
                break
            elif user_input == 3:
                print("Aborting :(")
                manager.close()
                socket.close()
                exit(-1)


        device = manager.device(portInfo.deviceId())
        if device is None:
            continue

        deviceList.append(device)
        print(f"Found a device with Tag: {device.deviceTagName()} @ address: {address}")

        filterProfiles = device.getAvailableFilterProfiles()
        print("Available filter profiles:")
        for f in filterProfiles:
            print(f.label())

        print(f"Current profile: {device.onboardFilterProfile().label()}");
        if device.setOnboardFilterProfile("General"):
            print("Successfully set profile to General");
        else:
            print("Setting filter profile failed!");

        print("Setting quaternion CSV output")
        device.setLogOptions(xsensdot_pc_sdk.XsLogOptions_Quaternion)

        logFileName = "logfile_" + portInfo.bluetoothAddress().replace(':', '-') + ".csv"
        print(f"Enable logging to: {logFileName}")
        if not device.enableLogging(logFileName):
            print(f"Failed to enable logging. Reason: {manager.lastResultText()}")

        print("Putting device into Quaternion measurement mode.")
        if not device.startMeasurement(xsensdot_pc_sdk.XsPayloadMode_ExtendedQuaternion):
            print(f"Could not put device into measurement mode. Reason: {manager.lastResultText()}")
            continue

    print("\nMain loop. Recording data for 10 seconds.")
    print("-----------------------------------------")

    # First printing some headers so we see which data belongs to which device
    s = ""
    for device in deviceList:
        s += f"{device.portInfo().bluetoothAddress():42}"
    print("%s" % s, flush=True)

    orientationResetDone = False
    startTime = xsensdot_pc_sdk.XsTimeStamp_nowMs()
    while xsensdot_pc_sdk.XsTimeStamp_nowMs() - startTime <= 10000:
        if callback.packetsAvailable():
            s = ""
            quaternion_data=[]
            for device in deviceList:
                # Retrieve a packet
                packet = callback.getNextPacket(device.portInfo().bluetoothAddress())

                if packet.containsOrientation():
                    quaternion = packet.orientationQuaternion()
                    quaternion_data_string = {quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]}
                    #Send quaternions to socket
                    quaternion_data_string = "  ".join(quaternion_data)
                    print(quaternion_data_string)
                    socket1.send(quaternion_data_string.encode())

            if quaternion_data:
                print("  ".join(quaternion_data))

            print("%s\r" % s, end="", flush=True)

            if not orientationResetDone and xsensdot_pc_sdk.XsTimeStamp_nowMs() - startTime > 5000:
                for device in deviceList:
                    print(f"\nResetting heading for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
                    if device.resetOrientation(xsensdot_pc_sdk.XRM_Heading):
                        print("OK", end="", flush=True)
                    else:
                        print(f"NOK: {device.lastResultText()}", end="", flush=True)
                print("\n", end="", flush=True)
                orientationResetDone = True
    print("\n-----------------------------------------", end="", flush=True)

    for device in deviceList:
        print(f"\nResetting heading to default for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
        if device.resetOrientation(xsensdot_pc_sdk.XRM_DefaultAlignment):
            print("OK", end="", flush=True)
        else:
            print(f"NOK: {device.lastResultText()}", end="", flush=True)
    print("\n", end="", flush=True)

    print("\nStopping measurement...")
    for device in deviceList:
        if not device.stopMeasurement():
            print("Failed to stop measurement.")
        if not device.disableLogging():
            print("Failed to disable logging.")

    print("Closing ports...")
    manager.close()

    print("Successful exit.")

    #Close socket
    socket1.close()

