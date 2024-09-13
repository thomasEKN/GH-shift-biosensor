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
from Analytics import *


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
    
    # set opertaing mode
    device_PSD.SetOperatingMode(PositionAlignerStatus.OperatingModes.Monitor, False)
    
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

def ConnectMotor(portNum):
    
    # portNum: port number which the motor is connected to (must be string)
    
    motor_uri = "xi-com:\\\\.\\COM" + portNum       # Serial port
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

def test_info(lib, device_id):
    print("\nGet device info")
    x_device_information = device_information_t()
    result = lib.get_device_information(device_id, byref(x_device_information))
    print("Result: " + repr(result))
    if result != Result.Ok:
        print("Device information:")
        print(" Manufacturer: " +
                repr(string_at(x_device_information.Manufacturer).decode()))
        print(" ManufacturerId: " +
                repr(string_at(x_device_information.ManufacturerId).decode()))
        print(" ProductDescription: " +
                repr(string_at(x_device_information.ProductDescription).decode()))
        print(" Major: " + repr(x_device_information.Major))
        print(" Minor: " + repr(x_device_information.Minor))
        print(" Release: " + repr(x_device_information.Release))

def test_status(lib, device_id):
    print("\nGet status")
    x_status = status_t()
    result = lib.get_status(device_id, byref(x_status))
    print("Result: " + repr(result))
    if result != Result.Ok:
        print("Status.CurSpeed: " + repr(x_status.CurSpeed))
        print("Status.Upwr: " + repr(x_status.Upwr))
        print("Status.Iusb: " + repr(x_status.Iusb))
        print("Status.Flags: " + repr(hex(x_status.Flags)))