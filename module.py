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
    # piezo: piezo controller object
    # lockIn: lock-in amplifier object
    # positions: numpy array of piezo stage positions at which measurements are taken
    # name of variable/polarisation state i.e TM_YDIFF or TE_YDIFF
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
    
    for v in voltages:
            
        
        # move stage
        #print("\nMoving stage to next position...")
        newVoltage = Decimal(v)
        piezo.SetOutputVoltage(newVoltage)
        time.sleep(0.5)
        print(f'Moved to {piezo.GetOutputVoltage()}')

        # allow lock in amp to lock in to new signal
        print("Taking measurement..")
        time.sleep(1.5)

        # take many readings and average
        TE_data, TM_data = dualAvgLockInReading(lockIn1, lockIn2, 5)

        # store mean and SD for each state
        TM_signal.append(TM_data[0])
        TM_errors.append(TM_data[1])

        TE_signal.append(TE_data[0])
        TE_errors.append(TE_data[1])
        
        print("TM Signal: {}\n".format(TM_data[0]))
        print("TE Signal: {}\n".format(TE_data[0]))
    
    # return piezo displacement to zero 
    piezo.SetZero()
    time.sleep(0.5)

    return TM_signal, TM_errors, TE_signal, TE_errors
    


def linearFunc(x, a, b):
    # x: independent variable
    # a: first parameter 
    # b: 2nd parameter (y-intercept)
    # provides function for use in linear regression 
    #
    
    out = (a * x) + b
    
    return out

def getAvgLockInReading(lockIn, period):
    # lockIn: lock in amplifier object
    # period: length of time to take measurements for

    # takes multiple readings from lock-in and 
    # returns the mean and standard deviation.
    # A latency period of 0.1s is chosen to limit the
    # speed of communication with the lock-in
    
    now = 0
    readings = []
    #print("Taking reading...\n")

    # take continuous measurements until period is over
    start = timer()
    while now < period:

        # take reading
        sign = np.sign(float(lockIn.query("OUTP? 1")))
        value = sign * 2 * float(lockIn.query("OUTP? 3")) # get magnitude
        readings.append(value)

        # latency interval
        time.sleep(0.1)

        # update current time
        now = timer()-start

    mean = np.mean(readings)
    stdev = np.std(readings)

    return mean, stdev


def dualAvgLockInReading(lockIn1, lockIn2, period):
    # lockIn: lock in amplifier object
    # period: length of time to take measurements for

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
        value1 = sign * 2 * float(lockIn1.query("OUTP? 3")) # get magnitude
        
        sign = np.sign(float(lockIn2.query("OUTP? 1")))
        value2 = sign * 2 * float(lockIn2.query("OUTP? 3")) 
        
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


def estimateShift(piezo, amp1, amp2, numScans, positions):
    # piezo: piezo controller object
    # amp: lock in amplifier object
    # numScans: number of beam scans to perform
    # 
    # estimateShift runs multiple beam scans and returns the 
    # estimated GH shift value for each. Each scan is used to 
    # iteratively determine the x-intercept of each state, 
    # which is used to narrow down the optimal range of
    # positions at which to take measurements.
    # [output]: 
    # estimates: estimated GH shift value for each scan

    estimates = []
    TM_fitParams = np.zeros([numScans, 2])
    TE_fitParams = np.zeros([numScans, 2])
    i=0

    # scan beams multiple times and calculate GH shift
    for scan in np.arange(numScans):
        
        print(f"Scan {i+1}\n")
        
        # run scan
        TM_signal, TM_err, TE_signal, TE_err = dualBeamScan(amp1, amp2, positions, piezo)

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
    
    return estimates, TM_fitParams, TE_fitParams

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


def calcCV(signal):

    std = np.std(signal)
    avg = np.mean(signal)

    cv = std/avg 

    return cv

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




def meanFilterConv(data, filter_size):
    #
    # Output: Returns numpy array of data convolved with mean 
    # filter of specified size. Since the output of the convolution 
    # is smaller than the input, lost data must be returned
    #
    # Args
    #   data - Input data to be filtered
    #   filter_size - size of filter 
    #
    mean_filter = [1/filter_size]*filter_size
    convData = np.convolve(data,mean_filter, mode='valid')

    # Resize data to fit original array
    overlap = round((filter_size-1)/2)
        
    # Recover lost data
    removed = np.delete(data, np.arange(overlap, len(data)-overlap, 1))
        
    # Insert filtered data between lost data
    out = np.insert(removed, overlap, convData)
    
    return out




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




def normZScore(data):

    # calculates z-score normalisation of data

    avg = np.mean(data)
    
    stdev = np.std(data)

    out = (data-avg)/stdev

    return out

def normalizeData(data):

    # normalizes data

    out = data / np.sum(data)

    return out

def gradientShiftEstimate(TM_signal, TE_signal):

    # initialize gradient constants
    TM_m = -0.0003065
    TM_msd = 0.000078 
    TE_m = -0.0004368 
    TE_msd = 0.0000910 

    shift_estimates = []
    
    for i in range(0,len(TM_signal)):
        TM_xintercept = -TM_signal[i] / TM_m
        TE_xintercept = -TE_signal[i] / TE_m

        shift_estimates.append(TM_xintercept - TE_xintercept)

    return shift_estimates
        





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
        power, sd = takeAvgPowerMeasure(meter, mPeriod)
        time.sleep(0.2)
        power_measurements.append(power)
        power_stdevs.append(sd)
    
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

    return angles, power_measurements, power_stdevs




def AmpAngleScan(amp1, amp2, motor_id, angles):

    # Output: Scans each angle, returns avg power measurement for each angle
    # plots and saves output as csv
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
    
    print("\nStarting measurements")
    signal_amp1 = []
    signal_amp2 = []  
    
    # Repeat for each angle
    for a in angles:
        
        # Move to angle
        calib_move(lib, motor_id, a, calib, units)
        test_wait_for_stop(lib, motor_id, 100)
        calb_get_position(lib, motor_id, calib, units) 

        # wait for lock-in
        time.sleep(1.5)
            
        # Take signal measurement
        print("\nTaking power measurement")
        sign = np.sign(float(amp1.query("OUTP? 1")))
        value1 = sign * 2 * float(amp1.query("OUTP? 3")) # get magnitude
        
        sign = np.sign(float(amp2.query("OUTP? 1")))
        value2 = sign * 2 * float(amp2.query("OUTP? 3")) 
        
        signal_amp1.append(value1)
        signal_amp2.append(value2)

    print("Scan finished\n")

    return signal_amp2, signal_amp1, 


def plotFittedData(angles, powerVals, stdevs):
    
    # Output: A plot of power against angle
    #
    # Args
    # 
    # angles: A list of the scanned angles 
    # power: list of power measurements for each angle

    # Create plot
    fig, ax = plt.subplots()
    
    # Fit curve to data
    #try:
    #x_points, fitted_curve = fitCurve(angles, powerVals)
    #ax.plot(x_points, fitted_curve, c='red')
    
        #print("Curve fitting failed")
        #time.sleep(1)

    # Plot data
    ax.errorbar(angles, powerVals, stdevs, fmt='o', mfc='blue', color='black', markersize=5)
    
    # Plot
    ax.grid()
    ax.set_xlabel('Angle (deg)')
    ax.set_ylabel('Power (W)')
    plt.show()
    
    return fig



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



def asymmetricFunc(x, a, b, c, d, e):
    return (a * (1 - (b + c * (x - d)))) / ((x - d)**2 + e**2)

def lorentzian(theta, I0, theta0, Gamma, Ibg):
    return I0 * (Gamma**2 / ((theta - theta0)**2 + Gamma**2)) + Ibg

def takeAvgPowerMeasure(meter, mPeriod):
    
    # Output: The mean of 10000 samples for duration mPeriod

    # Args
    #
    # meter: power meter object
    # mPeriod: time period of measurement in ms, must be integer
    #
    # The max measurement period is 100ms 
    # so averaging must be used for longer mPeriods

    if mPeriod < 100:
        mPeriod = 100
    
    # Set measurement parameters
    averaging = round(mPeriod/100) # Frequency of sample averaging (2 = 50KHz sampling, 4 = 25KHz sampling etc.)
    meter.confPowerMeasurementSequence(averaging) 

    # Start measurement sequence
    autoTriggerDelay = 0
    triggerForced = meter.startMeasurementSequence(autoTriggerDelay)

    # Set number of measurements
    baseTime = 100
    dataSize = baseTime * 100 # Max number of measurements is 10,000

    timeStamps = (c_float * dataSize)()
    data = (c_float * dataSize)() 
    meter.getMeasurementSequence(baseTime, timeStamps, data, None)   
    
    meanPower = np.mean(data)
    sdPower = np.std(data)
    print("\nMean: " + str(meanPower))
    
    return meanPower, sdPower



