import pyvisa
import time
from PyTLPMX import TLPMX
import numpy as np
import clr
from matplotlib import pyplot as plt
from datetime import datetime
from timeit import default_timer as timer
from numpy.linalg import lstsq
from scipy.optimize import curve_fit

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PositionAlignerCLI")

# Import
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.PositionAlignerCLI import *
from System import Decimal
from PyTLPMX import TLPMX
from ctypes import * 
from pyximc import *


def main():
    
        # Connect to LI-AMP    
        rm = pyvisa.ResourceManager()
        print(rm.list_resources())
        liamp = connectLIA(rm)  
        

        # Connect to power meter
        #pm5020 = ConnectDevice()
        

        # Connect to rotation stage
        #motor_id = ConnectMotor()
        

        # connect to KPA
        #device_PSD = connectPSD()
        

        # num = 10
        # yPositions_TM = []
        # yPositions_TE = []
        
        # for i in range(num):
        #     time.sleep(1) 
        #     xPos, yPos, quadSum = get_beam_coords(device_PSD)
        #     print("\nY Pos: {0}".format(yPos))
        #     yPositions_TM.append(yPos)
                       

            
            
        # input("Now swap to TE...\n")
        
        # for i in range(num):
        #     time.sleep(1) 
        #     xPos, yPos, quadSum = get_beam_coords(device_PSD)
        #     yPositions_TE.append(yPos)
                       

        #     print("\nY Pos: {0}".format(yPos))
        
        # shift = np.mean(yPositions_TM) - np.mean(yPositions_TE)
        
        # print(shift)

        # Get ydiff from position aligner
        # timeInt = int(input("Time to centre: "))
        # centreBeam(device_PSD, timeInt)
        
        
        # Set auto phase
        # print("\nSetting auto-phase...")
        # liamp.write("APHS")
        # time.sleep(10)



    
        # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



        
        # # FOR EACH POL STATE TAKE SCANS OF YDIFF AND SUM
        
        # # Initialize parameters
        # start = 44
        # end = 45
        # step = 0.5
        
        # # Set lock-in to expand (convert to mv for more precise reading)
        # #liamp.write("E 1 1")

        # # [Connect YDIFF output of KPA to A input of lock-in]
        # print("Ensure the YDIFF output of the KPA is connected to the input of the lock-in")
        # input("Press enter to confirm only the TM state is passing through the chopper stage...")
        # variable = "TM YDIFF"
        # angles, TE_ydiffs = runLockInScan(liamp, motor_id, start, end, step, variable)
        
        # # Switch polarization states and repeat
        # input("TM YDIFF SCAN COMPLETED\nOnce you have switched the polarisation state to TE, press enter...")

        # variable2 = "TE YDIFF"
        # angles, TM_ydiffs = runLockInScan(liamp, motor_id, start, end, step, variable2)
        
        #  # Switch to sum output of position aligner
        # input("Now connect the sum output of the KPA to the lock-in, then press enter to confirm...")
        
        # # Set auto-phase after switching input to ensure output is positive
        # print("\nSetting auto-phase...")
        # liamp.write("APHS")
        # time.sleep(10)    
       
        # variable3 = "TE SUM"
        # angles, TE_sums = runLockInScan(liamp, motor_id, start, end, step, variable3)
        
        # # Switch polarization states and repeat
        # input("Finally, switch the polarisation state to TM and then press enter to confirm...")
        
        # # Set auto-phase after switching state to ensure output is positive
        # print("\nSetting auto-phase...")
        # liamp.write("APHS")
        # time.sleep(10)
        
        # variable4 = "TM SUM"
        # angles, TM_sums = runLockInScan(liamp, motor_id, start, end, step, variable4)
        
        # print("Scans completed. Calculating shift and saving data...")
        
        # #Calculate position of each reading
        # TE_pos = np.divide(TE_ydiffs, TE_sums)
        # TM_pos = np.divide(TM_ydiffs, TM_sums)
            
        # # Calculate shifts
        # shifts = np.subtract(TE_pos, TM_pos)
        
        # # Convert to micrometres and multiply by radius of quadrant detector
        # conv_factor = 1000 * 4.9
        # shifts_micro = np.multiply(shifts, conv_factor)
        
        # # Plot shifts
        # fig = plotData(angles, shifts_micro, "Dte - Dtm (um)")
        
        # # Save data
        # now = datetime.now()
        # current_time = now.strftime("%H;%M")
        # file_prefix = "{}-{}-{}-{}-".format("GH_SHIFTS", start, end, step) + current_time 
        # figName = file_prefix + ".png"
    
        # # Save fig to png in figs folder
        # os.chdir("Figs")
        # fig.savefig(figName)
        # os.chdir("..")
    
        # # Save data to csv
        # saveDataCSV(angles, shifts_micro, file_prefix)
        

        # os.chdir("CSVs")
        # csvFileName = file_prefix + ".csv"
        # with open(csvFileName, "w") as txt_file:
	       #  for i in range(len(angles)):
        #         #txt_file.write("angles,TM_ydiffs,TE ydiffs,TM sums,TE sums,GH shifts\n")        
		      #   txt_file.write("{}".format(angles[i]) + "," + "{:e}".format(TM_ydiffs[i]) + "," + "{:e}".format(TE_ydiffs[i]) + "," + "{:e}".format(TM_sums[i]) + "," + "{:e}".format(TE_sums[i]) + "," + "{:e}".format(shifts[i]) + "\n")
    
        # # Return to main folder
        # os.chdir("..")


        # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        # RUN BEAM SCAN FOR EACH STATE

        

        # initialize stage position vector
        # One full revolution on the micrometer (fine spindle) is 50um, with each graduation representing 1um
        positions = np.array(np.linspace(0,40,21))
        
        # run scan
        TM_ydiffs, TM_alpha, TM_cov =  runBeamScan(liamp, positions)
        print("TM Alpha: {}\n".format(TM_alpha))
        # Switch states
        input("\nNow switch state to TE before proceeding...")
        
        # scan TE state
        TE_ydiffs, TE_alpha, TE_cov =  runBeamScan(liamp, positions)
        print("TE Alpha: {}\n".format(TE_alpha))


        # PLOT RESULTS
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(positions, TM_ydiffs, '.', color="purple")
        TM_fit = TM_alpha[0]*np.array(positions) + TM_alpha[1]
        ax.plot(positions, TM_fit, 'b')
        
        ax.plot(positions, TE_ydiffs, '.', color="orange")
        TE_fit = TE_alpha[0]*np.array(positions) + TE_alpha[1]
        ax.plot(positions, TE_fit, 'r')        

        ax.set_xlabel('Stage position (um)')
        ax.set_ylabel('Signal (V)')
        ax.grid()
         
        # add legend
        legend_drawn_flag = True
        plt.legend(["TM YDIFF", "TM fit","TE YDIFF", "TE fit"], loc=0, frameon=legend_drawn_flag)

        plt.show()
        
        


        # calculate x intercepts and get GH shift
        TM_intercept = -TM_alpha[1] / TM_alpha[0]
        TE_intercept = -TE_alpha[1] / TE_alpha[0]
        
        shift = TM_intercept - TE_intercept
        print("\nShift: {}".format(shift))

        # save data to csv
        now = datetime.now()
        current_time = now.strftime("%H;%M")
        file_prefix = "{}-".format("BEAM_SCAN_DATA") + current_time
        
        figName = file_prefix + ".png"
    
        # Save fig to png in figs folder
        os.chdir("Figs")
        fig.savefig(figName)
        os.chdir("..")
        
        # Save to CSV in csv folder
        os.chdir("CSVs")
        csvFileName = file_prefix + ".csv"
        with open(csvFileName, "w") as txt_file:   
	        for i in range(len(positions)):
		        txt_file.write("{}".format(positions[i]) + "," + "{:e}".format(TM_ydiffs[i]) + "," + "{:e}".format(TE_ydiffs[i]) + "\n")
    
        # Return to main folder
        os.chdir("..")
        
        # # Disconnect devices
        print("Disconnecting devices...")
        # #meter.close()
        # lib.close_device(byref(c_int(motor_id)))
        #device_PSD.Disconnect()
        
    #except:
        # print("Fail")
        # print("Disconnecting devices...")
        # #meter.close()
        # lib.close_device(byref(c_int(motor_id)))
        # #device_PSD.Disconnect()
        
    
    





# Connect to LIAMP
# Write function that: 
#    - sets Auto phase
#    - takes CH1 output measurement (query("OUTP? 1"))
#    - converts voltage to power (v * getPowerRange), this gives us the difference in watts between each pol state

def connectLIA(rm):
  
    inst = rm.open_resource('GPIB0::8::INSTR')
    
    return inst

def ConnectDevice():
    
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

def measureLockInNoise(liamp, pr):
    
    liamp.write("DDEF 1 ,2, 0")
    liamp.write("DDEF 2 ,2, 0")
    time.sleep(1)
        
    xn = float(liamp.query("OUTR? 1")) * pr
    yn = float(liamp.query("OUTR? 2")) * pr
        
    noise = np.sqrt(xn**2 +yn**2) 
        
    print(p)
    print(noise)

def takeLockInPowerMeasure(powMeter, liamp):
    #
    # Output: the power difference
    #
    # Args:
    #   powMeter: power meter object
    #   liamp: lock in amplifier object
    #
            
    # The magnitude R displayed by the power meter is the amplitude of the measured signal 
    # as a percentage of its total full scale range. This depends on the range settings on the power meter


    # Query R (magnitude of signal)
    r = float(liamp.query("OUTP? 3"))
    
    # Get full scale range and output voltage from PM
    pm_range = powMeter.getPowerRange(0)
    pow_diff = r * pm_range

    return pow_diff
    



def trackNoise(meter, liamp):
    # Measure the standard deviation of data across time
    # Plots data
    
    stdevs = []
    tStamps = []
    t=1
    
    # Intialise plot
    fig, ax = plt.subplots()
    ax.set_ylabel("Standard deviation")
    ax.set_xlabel("Time")
    ax.grid()
    
    while t <= time:
        # Take power, get sd
        p, sd = takeLockInPowerMeasure(meter, liamp)
        print("{} seconds".format(t))
        tStamps.append(t)
        stdevs.append(sd)
        ax.plot(tStamps, stdevs, "r-o")
        plt.pause(0.05)
        
        t += 1
        
    ax.plot(tStamps, stdevs, "r-o")
    print("Mean std: {}".format(np.mean(stdevs)))
    plt.show()
      


def calib_move(lib, device_id, position, calb, unit):
    print("\nMoving to {0} {1}".format(position, unit))
    result = lib.command_move_calb(device_id, c_float(position), byref(calb))
    if result != 0:
        print("Result: " + repr(result))

def calib_movr(lib, device_id, shift, calb, unit):
    print("\nMoving by {0} {1}".format(shift, unit))
    result = lib.command_movr_calb(device_id, c_float(shift), byref(calb))
    if result != 0:
        print("Result: " + repr(result))
    

def calb_get_position(lib, device_id, calb, units):
    print("\nRead position")
    pos = get_position_calb_t()
    result = lib.get_position_calb(device_id, byref(pos), byref(calb))
    if result != 0:
        print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} {1} ".format(pos.Position, units))
    return pos.Position


def test_wait_for_stop(lib, device_id, interval):
    print("\nWaiting for stop")
    result = lib.command_wait_for_stop(device_id, interval)
    if result != 0:
        print("Result: " + repr(result))

def centreBeam(psd, time_interval):
    # Takes measurements from the psd and averages them over time
    # checks if user is satisfied with proximity to zero
    # if not then repeat
    # PSD: psd object
    # time_interval: time to record for
    diff_vals = []
    num_measures = 20
    start = timer()
    now = 0
    while now < time_interval:
        
        # Get ydiff
        status = psd.Status
        yDiff = status.PositionDifference.Y
        diff_vals = np.append(diff_vals, yDiff)
        
        # Take moving average of last few measurements
        moving_avg = np.mean(diff_vals[-num_measures:])
        
        # Update console showing new value
        print(f"\r{moving_avg}", end="")
        
        time.sleep(0.1)
        now = timer() - start
        
    print("\nDone")
    print("\n Overall avg: {}".format(np.mean(diff_vals)))
    
def connectPSD():
    
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

def runLockInScan(lockIn, motor_id, start, end, step, var_name):
    
    # Output: Scans each angle, returns magnitude output of lock-in 
    # Args
    # 
    # lockIn: lockin object
    # motor_id: ID of motor stage
    # Start: Start of arc (degrees)
    # End: End of arc (degrees)
    # step: step size (degrees)
    # var: name of variable being measured

    # Set fixed parameters
    units = "degrees"
    calib = calibration_t()
    calib.A = c_double(0.01)   
    calib.MicrostepMode = 9    
    
    print("\nStarting measurements")
    readings = [] 
    
    angles = np.arange(start, end+step, step)
    
    # Repeat for each angle
    for a in angles:
        
        # Move to angle
        calib_move(lib, motor_id, a, calib, units)
        test_wait_for_stop(lib, motor_id, 100)
        calb_get_position(lib, motor_id, calib, units) 
        
        # Set auto phase
        print("\nLocking in...")
        time.sleep(6)
        
        # Take Lockin measurement
        print("\nTaking reading")
        
        # Get reading and convert to pk-pk Volts
        sign = np.sign(float(lockIn.query("OUTP? 1")))
        value = sign * 2 * float(lockIn.query("OUTP? 3"))
        #time.sleep(0.2)
        print("Reading: {}".format(value))

        readings.append(value)
    
    # Fit data to curve and plot
    fig = plotData(angles, readings, var_name)
    
    # Set file name prefix
    now = datetime.now()
    current_time = now.strftime("%H;%M")
    file_prefix = "{}-{}-{}-{}-".format(var_name, start, end, step) + current_time 
    figName = file_prefix + ".png"
    
    # Save fig to png in figs folder
    os.chdir("Figs")
    fig.savefig(figName)
    os.chdir("..")
    
    # Save data to csv
    saveDataCSV(angles, readings, file_prefix)
    
    return angles, readings

def saveDataCSV(angles, readings, file_prefix):
    
        # Output: None, saves data to csv in CSVs folder (must have csv folder in cwd)
        #
        # Args
        # 
        # angles: A list of the scanned angles 
        # power: list of power measurements for each angle   
        # stdevs: list of standard deviations for each measurement
        # file_prefix: file name for saved csv data
    
        # Save data to CSV 
        os.chdir("CSVs")
        csvFileName = file_prefix + ".csv"
        with open(csvFileName, "w") as txt_file:
	        for i in range(len(angles)):
		        txt_file.write("{}".format(angles[i]) + "," + "{:e}".format(readings[i]) + "\n")
    
        # Return to main folder
        os.chdir("..")

def plotData(angles, data, ylabel):
    
    # Plots data against angle
    # ylabel = string name for y-axis data

    fig, ax = plt.subplots()
    
    # Plot
    ax.plot(angles, data, "-o")
    ax.grid()
    ax.set_xlabel('Angle (deg)')
    ax.set_ylabel(ylabel)
    plt.show()
    
    return fig
    
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

def test_info(lib, device_id):
    print("\nGet device info")
    x_device_information = device_information_t()
    result = lib.get_device_information(device_id, byref(x_device_information))
    print("Result: " + repr(result))
    if result == Result.Ok:
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
    if result == Result.Ok:
        print("Status.CurSpeed: " + repr(x_status.CurSpeed))
        print("Status.Upwr: " + repr(x_status.Upwr))
        print("Status.Iusb: " + repr(x_status.Iusb))
        print("Status.Flags: " + repr(hex(x_status.Flags)))

def get_beam_coords(PSD):
    # Get position aligner status
    status = PSD.Status
    quadSum = status.Sum
    print("\n Getting beam coordinates...")
             
    # Get position and normalise
    xDiff = status.PositionDifference.X/quadSum
    yDiff = status.PositionDifference.Y/quadSum
          
    return xDiff, yDiff, quadSum

def runBeamScan(lockIn, positions):
    # lockIn: lock-in amplifier object
    # array of QPD translation stage positions at which measurements are taken
    # name of variable/polarisation state i.e TM_YDIFF or TE_YDIFF
    #
    # Takes Ydiff against stage position, measures from lock-in  
    # for each position (e.g every 100um), take ydiff measure
    # this should be done for both s and p states
    # fits straight line to data using least squares
    # plot and compare intercepts, where line crosses zero for each state
    # difference between intercepts in um is equal to GH shift
    
    # Set auto phase
    print("\nSetting auto-phase...")
    lockIn.write("APHS")
    time.sleep(10)

    yDiffs = []    
    input("Ensure beam is on positive end of QPD before proceeding with measurement...then press enter")
    
    for pos in positions:
            
        # move stage
        input("\nMove stage to next position, then press enter to proceed with next measurement\n")
        
        # wait
        print("Taking measurement..")
        #time.sleep(5)
        
        # take y-difference voltage
        sign = np.sign(float(lockIn.query("OUTP? 1")))
        ydiff = sign * 2 * float(lockIn.query("OUTP? 3"))
        yDiffs.append(ydiff)
        
        print("Signal: {}".format(ydiff))
    
   
    # perform least squares regression
    # Get parameters and covariance from curve_fit
    para, pcov = curve_fit(linearFunc, positions, yDiffs)
    
   
    return yDiffs, para, pcov
    

def linearFunc(x, a, b):
    # x: independent variable
    # a: first parameter 
    # b: 2nd parameter (y-intercept)
    # provides function for use in linear regression 
    #
    
    out = (a * x) + b
    
    return out

if __name__=="__main__":
    main()



# # The PM5020 outputs the power as a voltage from 0V to 2.5V proportional to the displayed reading
# # for the current full-scale range
# # For example, if the range is 0-250uW, and the power is 100uW, the voltage output will be 1V.
# # The LI-AMP displays voltages as a percentage of the full-scale range, which in our case is 2.5

# now i can measure power and remove the noise. 
# I should assess the extent of this noise reduction
# by using my measure noise function to take measurements with both the pm and the li, and compare noise levels
# also i can do experiments to see how the noise is affected