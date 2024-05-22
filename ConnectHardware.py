import pyvisa
import time
from PyTLPMX import TLPMX
import numpy as np
import clr
from matplotlib import pyplot as plt
from datetime import datetime
from timeit import default_timer as timer
from scipy.optimize import curve_fit

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericPiezoCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PositionAlignerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PiezoCLI.dll")

# Import CLIs
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.PositionAlignerCLI import *
from Thorlabs.MotionControl.KCube.PiezoCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI.Piezo import *
from System import Decimal 
from pyximc import *
from module import *


# LOCK-IN AMP

def connectLIA(rm):
    inst = rm.open_resource('GPIB0::8::INSTR')
    return inst









# POWER METER

def ConnectPM():
    
    meter = TLPMX()

    try:
        deviceCount = meter.findRsrc()
        resourceName = meter.getRsrcName(0)
        model, SN, mnfct, deviceAv = meter.getRsrcInfo(0)
        print(str(SN) + " is connected.")
        meter = TLPMX(resourceName, True, False)
    except:
        print("No Device Found!")

    return meter










# KPA Position Aligner

def connectKPA():
    
    # Initialise device
    serialPSD = str("69253257")
    device_PSD = KCubePositionAligner.CreateKCubePositionAligner(serialPSD)
    DeviceManagerCLI.BuildDeviceList()
    print("Connecting to device")
    device_PSD.Connect(serialPSD)
    
    # Start polling
    device_PSD.StartPolling(250)
    time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
    device_PSD.EnableDevice()
    time.sleep(0.25)  # Wait for device to enable
   
    # Get Device information
    print("Getting device info")
    device_info = device_PSD.GetDeviceInfo()
    print(device_info.Description)
    if not device_PSD.IsSettingsInitialized():    
            device_PSD.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device_PSD.IsSettingsInitialized() is True   
    
    return device_PSD









# PIEZO

def connectKPZ(serial):
    
    # Initialise device
    #serial = str("29252602")
    device_KPZ = KCubePiezo.CreateKCubePiezo(serial)
    DeviceManagerCLI.BuildDeviceList()
    print("Connecting to device")
    device_KPZ.Connect(serial)

    # Start polling and enable
    device_KPZ.StartPolling(250)  #250ms polling rate
    time.sleep(0.25)
    device_KPZ.EnableDevice()
    time.sleep(0.25)  # Wait for device to enable

     # Get Device information
    print("Getting device info")
    device_info = device_KPZ.GetDeviceInfo()
    print(device_info.Description)
    if not device_KPZ.IsSettingsInitialized():    
            device_KPZ.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device_KPZ.IsSettingsInitialized() is True   

    # Device configuration must be loaded before any functions passed
    device_config = device_KPZ.GetPiezoConfiguration(serial)

    return device_KPZ







# MOTOR

def ConnectMotor():
    
    motor_uri = "xi-com:\\\\.\\COM3"      # Serial port
    # Get device ID
    motor_id = lib.open_device(motor_uri.encode())
    if motor_id > 0:
        print("Device with URI {} successfully opened".format(motor_uri))
    else:
        raise RuntimeError("Failed to open device with URI", motor_uri)
    
    # Get device info
    test_info(lib, motor_id)
    test_status(lib, motor_id)
    
    return motor_id

