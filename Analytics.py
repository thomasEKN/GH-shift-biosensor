import pyvisa
import time
import numpy as np
import clr
from matplotlib import pyplot as plt
from datetime import datetime
from timeit import default_timer as timer
from scipy.optimize import curve_fit
import csv
from System import Decimal 







def draw_normal_samples(mean, std_dev, n):
    # Generate n random numbers from a normal distribution
    samples = np.random.normal(loc=mean, scale=std_dev, size=n)
    return samples

def write_array_to_csv(filename, header_names, data):
    # Check if the length of header_names matches the number of columns in data
    if len(header_names) != len(data):
        raise ValueError("The number of header names must match the number of columns in data.")
    
    # Transpose the data to get rows instead of columns
    transposed_data = list(zip(*data))
    
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        # Write the header
        csv_writer.writerow(header_names)
        # Write the data rows
        csv_writer.writerows(transposed_data)
        
        
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



def asymmetricFunc(x, a, b, c, d, e):
    return (a * (1 - (b + c * (x - d)))) / ((x - d)**2 + e**2)

def lorentzian(theta, I0, theta0, Gamma, Ibg):
    return I0 * (Gamma**2 / ((theta - theta0)**2 + Gamma**2)) + Ibg


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


def calcCV(signal):

    # calculates the coefficient of variation of a signal
    
    std = np.std(signal)
    avg = np.mean(signal)

    cv = std/avg 

    return cv



def linearFunc(x, a, b):
    # x: independent variable
    # a: first parameter 
    # b: 2nd parameter (y-intercept)
    # provides function for use in linear regression 
    #
    
    out = (a * x) + b
    
    return out




def lineFit(xdata,ydata):
    # takes in experimental data and fits it to a 
    # linear regression line
    # [fit]: numpy array of fitted points to plot against xdata 
    # [parameters]: gradient and y-intercept
    
    parameters, covariances = curve_fit(linearFunc, xdata, ydata)
    fit_array = parameters[0]*np.array(xdata) + parameters[1]
    
    return fit_array, parameters

