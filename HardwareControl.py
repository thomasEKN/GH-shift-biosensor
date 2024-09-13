import pyvisa
import time
from PyTLPMX import TLPMX
import numpy as np
import clr
from matplotlib import pyplot as plt
from datetime import datetime
from timeit import default_timer as timer
from scipy.optimize import curve_fit
import csv

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

    

def measure_power(powMeter):
    power = c_double()
    powMeter.measPower(byref(power))
    return power

def avg_power(powMeter, numMeasures, latency):
    # powMeter = power meter object
    # numMeasures = number of measurements per average
    # latency = time between each measurement in ms

    powerVals = []
    # measure power num times and store in array
    for i in range(numMeasures):
        p = measure_power(powMeter)
        time.sleep(latency)
        powerVals.append(p.value)
        
    # return mean 
    return np.mean(powerVals)



def calib_move(lib, device_id, position, calb, unit):
    #print("\nMoving to {0} {1}".format(position, unit))
    result = lib.command_move_calb(device_id, c_float(position), byref(calb))
    if result != 0:
        print("Result: " + repr(result))

def calib_movr(lib, device_id, shift, calb, unit):
    print("\nMoving by {0} {1}".format(shift, unit))
    result = lib.command_movr_calb(device_id, c_float(shift), byref(calb))
    if result != 0:
        print("Result: " + repr(result))
    

def calb_get_position(lib, device_id, calb, units):
    #print("\nRead position")
    pos = get_position_calb_t()
    result = lib.get_position_calb(device_id, byref(pos), byref(calb))
    if result != 0:
        print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} {1} ".format(pos.Position, units))
    return pos.Position


def test_wait_for_stop(lib, device_id, interval):
    #print("\nWaiting for stop")
    result = lib.command_wait_for_stop(device_id, interval)
    if result != 0:
        print("Result: " + repr(result))

    
def rotateToPosition(motor_id, position):
    # A function which just moves the rotation stage to where you want without all the hassle
    # position = angle to move to in degrees
    
    # set units
    units = "degrees"
    calib = calibration_t()
    calib.A = c_double(0.01)   
    calib.MicrostepMode = 9
    
    # move stage
    calib_move(lib, motor_id, position, calib, units)
    test_wait_for_stop(lib, motor_id, 100)
    
    #return new position
    calb_get_position(lib, motor_id, calib, units)
    
    
    
def rotate(motor_id, n_degrees):
    # A function which just moves the rotation stage by n degrees
    # position = angle to move to in degrees
    
    # set units
    units = "degrees"
    calib = calibration_t()
    calib.A = c_double(0.01)   
    calib.MicrostepMode = 9
    
    # move stage
    calib_movr(lib, motor_id, n_degrees, calib, units)
    test_wait_for_stop(lib, motor_id, 100)
    
    #return new position
    calb_get_position(lib, motor_id, calib, units)   
    
    

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




def get_beam_coords(PSD):
    # Get position aligner status
    status = PSD.Status
    quadSum = status.Sum
    print("\n Getting beam coordinates...")
             
    # Get position and normalise
    xDiff = status.PositionDifference.X/quadSum
    yDiff = status.PositionDifference.Y/quadSum
          
    return xDiff, yDiff, quadSum
    


def dualBeamScan(lockIn1, lockIn2, positions, piezo):
    # [piezo]: piezo controller reference object
    # [lockIn]: lock-in amplifier reference objects (e.g L1, L2)
    # [positions]: numpy array of piezo stage positions (in microns)
    # at which measurements are taken. Max travel of piezo stage is 20um
    #
    # This function takes the signal from two lock-in amps, one for each polarisation state
    # Takes Ydiff signL for each stage position, for BOTH polarisation states simultaneously
    # measures signal from lock-in for each position (e.g every 1um)
    # fits straight line to data using least squares
    # plot and compare x intercepts, where line crosses zero for each state
    # difference between intercepts in um is equal to GH shift

    # Calculate piezo voltages needed to reach positions
    voltages = []
    voltages = positions/20 * 75

    TM_signal = []  
    TE_signal = []
    
    TM_errors = []
    TE_errors = []
    
    lockIn_time = 1.5
    avg_time = 5
    
    for v in voltages:
            
        
        # move stage
        #print("\nMoving stage to next position...")
        newVoltage = Decimal(v)
        piezo.SetOutputVoltage(newVoltage)
        time.sleep(0.5)
        print(f'Moved to {piezo.GetOutputVoltage()}V\n')

        # allow lock in amp to lock in to new signal
        print("Taking measurement..")
        time.sleep(lockIn_time)

        # take many readings and average
        TE_data, TM_data = dualAvgLockInReading(lockIn1, lockIn2, avg_time)

        # store mean and SD for each state
        TM_signal.append(TM_data[0])
        TM_errors.append(TM_data[1])

        TE_signal.append(TE_data[0])
        TE_errors.append(TE_data[1])
        
        #print("TM Signal: {}\n".format(TM_data[0]))
        #print("TE Signal: {}\n".format(TE_data[0]))
    print("Scan completed\n")
    
    # return piezo displacement to zero 
    piezo.SetZero()
    time.sleep(0.5)

    return TM_signal, TM_errors, TE_signal, TE_errors



def monoBeamScan(amp, positions, piezo):
    # [piezo]: piezo controller reference object
    # [lockIn]: lock-in amplifier reference objects (e.g L1, L2)
    # [positions]: numpy array of piezo stage positions (in microns)
    # at which measurements are taken. Max travel of piezo stage is 20um
    #
    # This function takes the signal from ONE lock-in amp,
    # Takes Ydiff signal for each stage position,
    # measures signal from lock-in for each position (e.g every 1um)
    
    # Calculate piezo voltages needed to reach positions
    voltages = []
    voltages = positions/20 * 75

    signal = []
    errors = []
    
    # set lock-in time and averaging time
    lockIn_time = 3
    avg_time = 6
    
    for v in voltages:
            
        
        # move stage
        #print("\nMoving stage to next position...")
        newVoltage = Decimal(v)
        piezo.SetOutputVoltage(newVoltage)
        time.sleep(0.5)
        print(f'Moved to {piezo.GetOutputVoltage()}V\n')

        # allow lock in amp to lock in to new signal
        print("Taking measurement..")
        time.sleep(lockIn_time)

        # take many readings and average
        data = monoAvgLockInReading(amp, avg_time)

        # store mean and SD for each state
        signal.append(data[0])
        errors.append(data[1])
        
        #print("TM Signal: {}\n".format(TM_data[0]))
        #print("TE Signal: {}\n".format(TE_data[0]))
    print("Scan completed\n")
    
    # return piezo displacement to zero 
    piezo.SetZero()
    time.sleep(0.5)

    return signal, errors
    

def signalScan(lockIn1, lockIn2, positions, piezo):
    # [piezo]: piezo controller reference object
    # [lockIn]: lock-in amplifier reference objects (e.g L1, L2)
    # [positions]: numpy array of piezo stage positions (in microns)
    # at which measurements are taken. Max travel of piezo stage is 20um
    #
    # This function takes the signal from two lock-in amps, one for each polarisation state
    # Takes Ydiff signL for each stage position, for BOTH polarisation states simultaneously
    # measures signal from lock-in for each position (e.g every 1um)
    # fits straight line to data using least squares
    # plot and compare x intercepts, where line crosses zero for each state
    # difference between intercepts in um is equal to GH shift

    # Calculate piezo voltages needed to reach positions
    voltages = []
    voltages = positions/20 * 75

    scan_signal_2 = []  
    scan_signal_1 = []
    
    TM_data = []
    TE_data = []
    
    lockIn_time = 1.5
    avg_time = 5
    
    
    # record start time
    start = timer()
    t_stamps_all = np.array([])
    pos_t_stamps = []
    
    # for each stage position, monitor signal and record avg ydiff
    for v in voltages:
            
        
        # record timestamp
        now = timer() - start
        pos_t_stamps.append(now)
        
        # move stage
        #print("\nMoving stage to next position...")
        newVoltage = Decimal(v)
        piezo.SetOutputVoltage(newVoltage)
        time.sleep(0.2)
        print(f'Moved to {piezo.GetOutputVoltage()}V\n')

        # allow lock in amp to lock in to new signal
        print("Taking measurement..")
        #time.sleep(lockIn_time)

        # take many readings and average
        signal_1, signal_2, t_stamps = recordSignals(lockIn1, lockIn2, avg_time+lockIn_time)
        t_stamps = np.array(t_stamps)
        # add monitored signal to array
        scan_signal_1 = scan_signal_1 + signal_1
        scan_signal_2 = scan_signal_2 + signal_2
        
        TE_data.append(np.mean(signal_1))
        TM_data.append(np.mean(signal_2))
        
    
        
        # add timestamps to last set of timestamps for continuous monitoring
        if v==0:
            t_stamps_all = np.concatenate((t_stamps_all,t_stamps))
        else:
            t_stamps_all = np.concatenate((t_stamps_all, np.add(t_stamps,t_stamps_all[-1])))
        
    print("Scan completed\n")
    
    # return piezo displacement to zero 
    piezo.SetZero()
    time.sleep(0.5)

    return scan_signal_1, scan_signal_2, TE_data, TM_data, t_stamps_all, pos_t_stamps




def dualAvgLockInReading(lockIn1, lockIn2, period):
    # [lockIn]: lock in amplifier object
    # [period]: length of time to take measurements for

    # takes multiple readings from both lock-ins and 
    # returns the mean and standard deviation.
    # A latency period of 0.1s is chosen to limit the
    # speed of communication with the lock-in

    # Ouput
    # [data1]: mean and standard deviation of signal from lock-in 1
    # [data2]: mean and standard deviation of signal from lock-in 2
    
    now = 0
    signal_1 = []
    signal_2 = []
    
    # take continuous measurements until period is over
    start = timer()
    while now < period:

        # take reading
        sign = np.sign(float(lockIn1.query("OUTP? 1")))
        value1 = sign * float(lockIn1.query("OUTP? 3")) # get magnitude
        
        sign = np.sign(float(lockIn2.query("OUTP? 1")))
        value2 = sign * float(lockIn2.query("OUTP? 3")) 
        
        signal_1.append(value1)
        signal_2.append(value2)

        # latency interval
        time.sleep(0.1)

        # update current time
        now = timer()-start

    # Store means and standard deviations for each state in Nx2 matrices
    mean1 = np.mean(signal_1)
    stdev1 = np.std(signal_1)

    mean2 = np.mean(signal_2)
    stdev2 = np.std(signal_2)

    data1 = [mean1,stdev1]
    data2 = [mean2,stdev2]

    return data1, data2



def monoAvgLockInReading(amp, period):
    # [lockIn]: lock in amplifier object
    # [period]: length of time to take measurements for

    # takes multiple readings from ONE lock-in amp and 
    # returns the mean and standard deviation.
    # A latency period of 0.1s is chosen to limit the
    # speed of communication with the lock-in

    # Ouput
    # [data]: mean and standard deviation of signal from lock-in 

    
    now = 0
    signal = []
    
    # take continuous measurements until period is over
    start = timer()
    while now < period:

        # take reading
        sign = np.sign(float(amp.query("OUTP? 1")))
        value1 = sign * float(amp.query("OUTP? 3")) # get magnitude
        
        
        signal.append(value1)

        # latency interval
        time.sleep(0.1)

        # update current time
        now = timer()-start

    # Store means and standard deviations for each state in Nx2 matrices
    mean = np.mean(signal)
    stdev = np.std(signal)

    data = [mean,stdev]

    return data


def estimateShift(piezo, lockIn1, lockIn2, numScans, positions):
    # [piezo]: piezo controller object
    # [lockIn]: lock in amplifier object
    # [numScans]: number of beam scans to perform
    # 
    # estimateShift runs multiple beam scans and returns the 
    # estimated GH shift value for each. 
    # [output]: 
    # estimates: estimated GH shift value for each scan
    # fitParams: fitted linear regression parameters for each beam scan
    # timestamps: timestamp for start of each scan
    # errors: = summed error of each measurement

    estimates = []
    TM_fitParams = np.zeros([numScans, 2])
    TE_fitParams = np.zeros([numScans, 2])
    errors = []
    timestamps = []
    i=0
    t_start = timer()
    # scan beams multiple times and calculate GH shift
    for scan in np.arange(numScans):
        
        print(f"Scan {i+1}\n")
        
        # run scan
        elapsed = timer() - t_start
        timestamps.append(elapsed)
        TM_signal, TM_err, TE_signal, TE_err = dualBeamScan(lockIn1, lockIn2, positions, piezo)
        error_sum = np.sum(TM_err) + np.sum(TE_err)
        errors.append(error_sum)
        
        # fit data to line
        TM_para, TM_pcov = curve_fit(linearFunc, positions, TM_signal)
        TE_para, TE_pcov = curve_fit(linearFunc, positions, TE_signal)
        
        # save fitted line paramaters  
        TM_fitParams[i, 0] = TM_para[0]
        TM_fitParams[i, 1] = TM_para[1]
        TE_fitParams[i, 0] = TE_para[0]
        TE_fitParams[i, 1] = TE_para[1]
        
        # Calculate intercept for each state
        TM_intercept = -TM_para[1] / TM_para[0]
        TE_intercept = -TE_para[1] / TE_para[0]

        # Calculate shift
        shift = TM_intercept - TE_intercept
        print("shift: {}\n".format(shift))
        estimates.append(shift)

        i +=1
    
    return estimates, TM_fitParams, TE_fitParams, timestamps, errors



def estimateShift_MonoBeam(piezo, amp1, amp2, numScans, positions):
    # [piezo]: piezo controller object
    # [lockIn]: lock in amplifier object
    # [numScans]: number of beam scans to perform
    # 
    # estimateShift runs multiple beam scans and returns the 
    # estimated GH shift value for each. 
    # [output]: 
    # estimates: estimated GH shift value for each scan
    # fitParams: fitted linear regression parameters for each beam scan
    # timestamps: timestamp for start of each scan
    # errors: = summed error of each measurement

    estimates = []
    TM_fitParams = np.zeros([numScans, 2])
    TE_fitParams = np.zeros([numScans, 2])
    timestamps = []
    i=0
    t_start = timer()
    # scan beams multiple times and calculate GH shift
    for scan in np.arange(numScans):
        
        print(f"Scan {i+1}\n")
        
        # run scan
        elapsed = timer() - t_start
        timestamps.append(elapsed)
        # RUN BEAM SCAN for each beam
        input("Block out TE state then press enter to proceed...")
        TM_signal, TM_err = monoBeamScan(amp2, positions, piezo)
        
        input("Block out TM state then press enter to proceed...")
        TE_signal, TE_err = monoBeamScan(amp1, positions, piezo)
        
        # fit data to line
        TM_para, TM_pcov = curve_fit(linearFunc, positions, TM_signal)
        TE_para, TE_pcov = curve_fit(linearFunc, positions, TE_signal)
        
        # save fitted line paramaters  
        TM_fitParams[i, 0] = TM_para[0]
        TM_fitParams[i, 1] = TM_para[1]
        TE_fitParams[i, 0] = TE_para[0]
        TE_fitParams[i, 1] = TE_para[1]
        
        # Calculate intercept for each state
        TM_intercept = -TM_para[1] / TM_para[0]
        TE_intercept = -TE_para[1] / TE_para[0]

        # Calculate shift
        shift = TM_intercept - TE_intercept
        print("shift: {}\n".format(shift))
        estimates.append(shift)

        i +=1
    
    return estimates, TM_fitParams, TE_fitParams, timestamps



def recordSignals(amp1, amp2, period):
    # amp: lock in amplifier object
    # period: period of time to measure signals
    #
    # records signal from lock-ins for specific period of time
    
    # set time between measurements
    latency = 0.1

    # initialise arrays
    now = 0
    signal_amp1 = []
    signal_amp2 = []
    timestamps=[]
    
    # take continuous measurements until period is over
    start = timer()
    print(f"Starting {period} seccond measurement....")
    while now < period:
    
        timestamps.append(now)
        
        # take readings
        sign = np.sign(float(amp1.query("OUTP? 1")))
        value1 = sign * 2 * float(amp1.query("OUTP? 3")) # get magnitude
        
        sign = np.sign(float(amp2.query("OUTP? 1")))
        value2 = sign * 2 * float(amp2.query("OUTP? 3")) 

        # save result
        signal_amp1.append(value1)
        signal_amp2.append(value2)
    
        # latency interval before next measurement
        time.sleep(latency)
    
        # update current time
        now = timer()-start
        
    print("Done")
    
    return signal_amp1, signal_amp2, timestamps



def bestLockinParaEstimate(amp1, amp2, tcMax):

    # estimates the best parameter settings to use
    # on the lock-in that result in the lowest standard deviation
    #
    #
    
    # measure signal for 2 minutes at a time (120 seconds)
    period = 120
    slopeTime = [5, 7, 9, 10]
    sd_data = {
        "6": [0,0],
        "12": [0,0],
        "18": [0,0],
        "24": [0,0]
    }
    
    i = 0
    
    for slope in sd_data:

        # set slope parameter on lock-ins
        amp1.write(f"OFSL {i}")
        amp2.write(f"OFSL {i}")

        # allow appropriate lock-in time depending on time constant and slsope
        time.sleep(slopeTime[i]*tcMax)

        # measure signal for period of time
        signal_1, signal_2, timestamps = recordSignals(amp1, amp2, period)

        # calculate coefficient of variation
        sd1 = np.std(signal_1)
        sd2 = np.std(signal_2)

        # store values in dictionary
        sd_data[f"{slope}"] = [sd1,sd2]

        i +=1

    print("Finished")

    return sd_data





def recordSignalsAndPower(amp1, amp2, powMeter, period):
    # amp: lock in amplifier object
    # period: period of time to measure signals
    #
    # records signal from lock-ins for specific period of time
    
    # set time between measurements
    latency = 0.1

    # initialise arrays
    now = 0
    signal_amp1 = []
    signal_amp2 = []
    power = []
    timestamps=[]
    
    # take continuous measurements until period is over
    start = timer()
    print(f"Starting {period} seccond measurement....")
    while now < period:
    
        timestamps.append(now)
        
        # take readings
        sign = np.sign(float(amp1.query("OUTP? 1")))
        value1 = sign * 2 * float(amp1.query("OUTP? 3")) # get magnitude
        
        sign = np.sign(float(amp2.query("OUTP? 1")))
        value2 = sign * 2 * float(amp2.query("OUTP? 3")) 

        powerVal = powMeter.measPower()

        # latency interval before next measurement
        time.sleep(latency)

        # save result
        signal_amp1.append(value1)
        signal_amp2.append(value2)
        power.append(powerVal)
    
        # update current time
        now = timer()-start
        
    print("Done")
    
    return signal_amp1, signal_amp2, power, timestamps





    
    

def PMAngleScan(meter, motor_id, start, end, step, mPeriod):
    
    # Output: Scans each angle, returns avg power measurement for each angle
    # plots and saves output as csv
    #
    # Args
    # 
    # meter: power meter object
    # motor_id: 
    # Start: Start of arc (degrees)
    # End: End of arc (degrees)
    # step: step size (degrees)
    # mPeriod: Time spent on each measurement

    # Set fixed parameters
    units = "degrees"
    calib = calibration_t()
    calib.A = c_double(0.01)   
    calib.MicrostepMode = 9    
    
    print("\nStarting measurements")
    power_measurements = [] 
    power_stdevs = []
    angles = np.arange(start, end+step, step)
    
    # Repeat for each angle
    for a in angles:
        
        # Move to angle
        calib_move(lib, motor_id, a, calib, units)
        test_wait_for_stop(lib, motor_id, 100)
        calb_get_position(lib, motor_id, calib, units) 
        
        # Find correct range before starting measurement
        if a == angles[0]:
            meter.setPowerAutoRange(True)
            time.sleep(2)
            
            #auto range must be set to false before measurement sequence.
            meter.setPowerAutoRange(False)
        
        # Take power measurement
        print("\nTaking power measurement")
        power = measure_power(meter)
        time.sleep(0.2)
        power_measurements.append(power)
        
    
    # Fit data to curve and plot
    
    # Set file name prefix
    #now = datetime.now()
    #current_time = now.strftime("%H;%M")
    #file_prefix = "PM-{}-{}-{}-{}-".format(start, end, step, mPeriod/1000) + current_time 
    #figName = file_prefix + ".png"
    
    # Save fig to png in figs folder
    #os.chdir("figs")
    #fig.savefig(figName)
    #os.chdir("..")
    
    # Save data to csv
    #saveDataCSV(angles, power_measurements, power_stdevs, file_prefix)

    return angles, power_measurements





def AmpAngleScan(amp1, amp2, motor_id, angles, pm_range):

    # Output: Scans each angle, returns avg power measurement for each angle
    #
    # Args
    # 
    # amp[n]: lock-in amplifier resource
    # motor_id: motor rotation stage resource
    # angles: numpy array of angles to scan

    # Set fixed parameters
    units = "degrees"
    calib = calibration_t()
    calib.A = c_double(0.01)   
    calib.MicrostepMode = 9   
    
    lockin_time = 1.5
    avg_time = 5
    scan_time = ((lockin_time+avg_time)*len(angles)) / 60
    
    print(f"\nStarting measurements, estimated completion time {scan_time} minutes")
    signal_amp1 = []
    signal_amp2 = []  
    stdevs1 = []
    stdevs2 = []
    
    # Repeat for each angle
    for a in angles:
        
        # Move to angle
        calib_move(lib, motor_id, a, calib, units)
        test_wait_for_stop(lib, motor_id, 100)
        calb_get_position(lib, motor_id, calib, units) 

        # wait for lock-in
        time.sleep(lockin_time)
            
        # Take signal measurement
        print("\nTaking power measurement")
        
        data1, data2 = dualAvgLockInReading(amp1, amp2, avg_time)
        
        signal_amp1.append(data1[0])
        stdevs1.append(data1[1])
        
        signal_amp2.append(data2[0])
        stdevs2.append(data2[1])

    print("Scan finished\n")
    
    # adjust data to power meter scale range
    # divide by two to undo avg
    
    #signal_amp1 = np.multiply(signal_amp1*0.02, pm_range)
    #signal_amp2 = np.multiply(signal_amp2*0.02, pm_range)
    #stdevs1 = np.multiply(stdevs1*0.02, pm_range)
    #stdevs2 = np.multiply(stdevs2*0.02, pm_range)

    return signal_amp1, stdevs1, signal_amp2, stdevs2 



def AmpAngleScanStep(amp1, amp2, motor_id, angles, pm_range):

    # Output: For longer scans, or scans where the power meter needs to be moved for each measurement 
    # moves rotation stage, waits for user to move power meter, then takes measurement and repeats
    #
    # Args
    # 
    # amp[n]: lock-in amplifier resource
    # motor_id: motor rotation stage resource
    # angles: numpy array of angles to scan

    # Set fixed parameters
    units = "degrees"
    calib = calibration_t()
    calib.A = c_double(0.01)   
    calib.MicrostepMode = 9   
    
    lockin_time = 1.5
    avg_time = 8
    scan_time = ((lockin_time+avg_time)*len(angles)) / 60
    
    print(f"\nStarting measurements, estimated completion time {scan_time} minutes")
    signal_amp1 = []
    signal_amp2 = []  
    stdevs1 = []
    stdevs2 = []
    
    # Repeat for each angle
    for a in angles:
        
        # Move to angle
        calib_move(lib, motor_id, a, calib, units)
        test_wait_for_stop(lib, motor_id, 100)
        calb_get_position(lib, motor_id, calib, units) 
        
        input("Press enter once power meter is positioned...\n")

        # wait for lock-in
        print("\nTaking power measurement")
        time.sleep(lockin_time)
            
        # Take signal measurement
        
        data1, data2 = dualAvgLockInReading(amp1, amp2, avg_time)
        
        signal_amp1.append(data1[0])
        stdevs1.append(data1[1])
        
        signal_amp2.append(data2[0])
        stdevs2.append(data2[1])

    print("Scan finished\n")
    
    # adjust data to power meter scale range
    # divide by two to undo avg
    
    #signal_amp1 = np.multiply(signal_amp1*0.02, pm_range)
    #signal_amp2 = np.multiply(signal_amp2*0.02, pm_range)
    #stdevs1 = np.multiply(stdevs1*0.02, pm_range)
    #stdevs2 = np.multiply(stdevs2*0.02, pm_range)

    return signal_amp1, stdevs1, signal_amp2, stdevs2 


def getSensitivity(lockIn):
    
    # lockIn: lock in amplifier reference
    # retrieves sensitivity of
    
    
    ID = float(lockIn.query("SENS?"))
    
    return ID
    




def fitCurve(angles, powerVals):
    # Fits asymmetric curve to data
    # Output:
    #   x_vals - x points sampled from fitted curve (x vals)
    #   y_vals - data points for fitted curve (y vals)
    #
    # Args:
    #   angles: angles sampled in scan
    #   powerVals: measured power values at each angle
    
    # obtain optimised parameter values from asymmetric function
    #initial_guess = [1.0, 65.0, 0.5, 0.1]
    popt, pcov = curve_fit(lorentzian, angles, powerVals)
    
    y_vals = []
    x_vals = np.linspace(angles[0], angles[-1], 100)
    
    # Calculate function value at sampled angles
    y_vals = asymmetricFunc(x_vals, popt[0], popt[1], popt[2], popt[3], popt[4])
    
    return x_vals, y_vals





def read_csv_to_array(filename):
    """
    Reads a CSV file and returns a list of lists, where each list contains the values of a column.
    
    :param filename: The path to the CSV file.
    :return: A list of lists, where each list corresponds to a column in the CSV file.
    """
    columns = []
    
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        
    header = next(reader)
        # Iterate through each row in the reader
    for row in reader:
        # If columns is empty, initialize it with the appropriate number of empty lists
        if not columns:
            columns = [[] for _ in row]
                
        # Append each value to the corresponding column list
        for i, value in enumerate(row):
            columns[i].append(float(value))
    
    return columns



        
        
def monitorVoltageDiff(kcube, period):
    # kcube: kcube position aligner reference object
    # period: period of time to measure signal
    #
    # records x and y voltage difference signal directly from position detector for specific period of time
    
    # set time between measurements
    latency = 0.1

    # initialise arrays
    now = 0
    ydiff = []
    xdiff = []
    timestamps=[]
    positionDiffs = []
    
    # take continuous measurements until period is over
    start = timer()
    print(f"Starting {period} seccond measurement....")
    while now < period:
    
        timestamps.append(now)
        
        # take readings
        positionDiffs.append(kcube.Status.PositionDifference)
    
        # latency interval before next measurement
        time.sleep(latency)
    
        # update current time
        now = timer()-start
        
    for pos in positionDiffs:
        xdiff.append(pos.X)
        ydiff.append(pos.Y)
        
    print("Done")
    
    return xdiff, ydiff, timestamps



