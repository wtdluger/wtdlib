import os
from glob import glob
from pathlib import Path
import time
import datetime as dt
import operator
import functools
import json
import subprocess
import platform
import ast

import numpy as np
import pandas as pd

try:
    import pyperclip
except ImportError:
    print('pyperclip not installed.  Unable to run copydf() function.')

"""
    DateTime Functions
"""
def return_time_as_dt(path, time_stamp='mtime'):
    """
    Returns the modification time (mtime) or change time (ctime) of the path 
    as a datetime object

    If the path is a directory, returns a dataframe of the mtimes or ctimes
    of the files in the directory as a datetime object.
    
    paramters:
    time_stamp: default 'mtime'.  Can be set to 'ctime' if cha
    """
    def file_time(input_file, time_stamp=time_stamp):
        """
        local function to return file's ctime or mtime
        """
        if time_stamp == 'mtime':
            time_string = time.asctime(time.localtime(os.path.getmtime(input_file)))
        elif time_stamp == 'ctime':
            time_string = time.asctime(time.localtime(os.path.getctime(input_file)))
        else:
            time_string = time.asctime(time.localtime(os.path.getmtime(input_file)))
        year = int(time_string[-4:])

        month_string = time_string[4:7]
        if month_string == 'Jan':
            month = 1
        elif month_string == 'Feb': 
            month = 2
        elif month_string == 'Mar':
            month = 3
        elif month_string == 'Apr':
            month = 4
        elif month_string == 'May':
            month = 5
        elif month_string == 'Jun':
            month = 6
        elif month_string == 'Jul':
            month = 7
        elif month_string == 'Aug':
            month = 8
        elif month_string == 'Sep':
            month = 9
        elif month_string == 'Oct':
            month = 10
        elif month_string == 'Nov':
            month = 11
        elif month_string == 'Dec':
            month = 12
        else:
            month = 5

        date = int(time_string[8:10])

        hour = int(time_string[11:13])
        minute = int(time_string[14:16])
        second = int(time_string[17:19])

        return dt.datetime(year, month, date, hour, minute, second)
    
    if os.path.isfile(path):
        times = file_time(path, time_stamp=time_stamp)
    elif os.path.isdir(path):
        files = os.listdir(path)
        times = []
        for file in files:
            times.append(file_time(os.path.join(path, file)))
        times = pd.DataFrame(np.transpose([files, times]), columns = ['File Name', time_stamp])
    else:
        times = None
        
    return times

def date_to_datetime(tdy):
    """converts a datetime date object to a datetime datetime object"""
    tdy_dt = dt.datetime(tdy.year, tdy.month, tdy.day)
    return tdy_dt

def isdst(soonish):
    """
    Takes a datetime.datetime object or datetime.date object,
    and returns if the date occurs during Daylight Saving Time.
    """
    if isinstance(soonish, dt.datetime):
        soonish = soonish.date()
    year, weekno, dayofweek = soonish.isocalendar()
    if weekno > 10 and weekno < 45:
    # if the week is between the 2nd Sunday of March and the 2nd Sunday of November
        return True
    elif weekno == 10:
    # if the ISO week is the 2nd Sunday of March, check day of week
        if dayofweek == 7:
        # if Sunday
            return True
    elif weekno == 45:
    # if the ISO week is the 2nd Sunday of November, check day of week
        if dayofweek != 7:
        # if not Sunday
            return True
    return False
    
def daterange(start_date, end_date):
    """
    Returns a range of datetime date objects between start_date and
    end_date.  This is consistent with the built-in range function,
    including start_date, but excluding end_date in the iteration.
    
    Copied from stack overflow: 
    https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)

"""
    Math Functions
"""
def sumproduct(*lists):
    """
    sumproduct function from excel
    https://stackoverflow.com/questions/3849251/sum-of-products-for-multiple-lists-in-python
    """
    return sum(functools.reduce(operator.mul, data) for data in zip(*lists))

def find_nearest(a, a0):
    """
    https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    Finds the nearest value in an array of arbitrary dimension
    """
    idx = np.abs(a - a0).argmin()
    return a.flat[idx]

def factor(x):
    """
    This function takes an integer, x, and returns a numpy array
    of the factors of x.
    """
    factors = []
    for i in range(1, x + 1):
        if x % i == 0:
            factors.append(i)
    return factors

def is_prime(n):
    """
    Returns True if the input integer is prime
    Returns False if the input integer can be factored

    Modified for simplicity from a function found on stack exchagne:
    https://stackoverflow.com/questions/15285534/isprime-function-for-python-language
    """
    # If even or less than 2
    if n % 2 == 0 or n <= 2:
        return False
    # If Odd, determine if not prime
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def normalize_(img, scale=1.0, arr_type=float):
    """
    Function to normalize a numpy array.
    To Normalize a float array to a 0-255 integer scale
    (format for computer graphics): scale=255, arr_type=int.
    """
    img = scale*( img - img.min() )/(img.max() - img.min())
    return img.astype(arr_type)

def delta_theta(targetA, sourceA, unit='degree'):
    """
    Returns the diference between two angles
    https://stackoverflow.com/questions/1878907/the-smallest-difference-between-2-angles
    a = targetA - sourceA
    a = (a + 180) % 360 - 180
    Parameter: unit:
        degree (angles between 0 and 360)
        radian (angles between 0 and 2*np.pi)
        turn (angles between 0 and 1)
        gradian (angles between 0 and 400)
    """
    if unit=='degree':
        full = 360.0
    elif unit=='radian':
        full = 2*np.pi
    elif unit=='turn':
        full = 1.0
    elif unit=='gradian':
        full = 400.0
    else:
        full = 360.0
    half = full / 2.0

    a = targetA - sourceA
    a = (a + half) % full - half
    return np.abs(a)

def sig_figs(x, p):
    """
    Returns x rounded to the number of significant figures p.
    
    Function copied from stack overflow, and originally named signif(x, p)
    https://stackoverflow.com/questions/18915378/rounding-to-significant-figures-in-numpy
    """
    x = np.asarray(x)
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags

"""
    List and String Functions
"""
def parse_tuple(string):
    """
    Splits a string into a tuple
    https://stackoverflow.com/questions/16449184/python-converting-string-to-tuple-without-splitting-characters
    """
    try:
        s = ast.literal_eval(str(string))
        if type(s) == tuple:
            return s
        return
    except:
        return

def sort_list(unsorted_list, reverse=True):
    """
    Takes a nx1 list and uses the Python native sorted() function to sort it.
    """
    sorted_list = sorted(list(dict.fromkeys(unsorted_list)), reverse=reverse)
    return sorted_list

def unique_entries(lst):
    """
    Takes an input list, and returns unique
    entries within that list.
    """
    unique = list(dict.fromkeys(lst))
    return unique

def copydf(df, include_index=True):
    """
    This function uses the pyperclip module to 
    copy a Pandas DataFrame to the clipboard
    for pasting into Microsoft Excel, LibreOffice Calc, etc.
    """
    if type(df) != type(pd.DataFrame()):
        # If a list or numpy array is provided as
        # input, change to a Pandas DataFrame.
        df = pd.DataFrame(df)

    if include_index == True:
        # Ensure Index Column is Copied
        df = df.reset_index()
        to_clipboard = """"""
    
    # Copy Column Names
    for col in df:
        to_clipboard += str(col) + """\t"""
    to_clipboard += """\r"""
    
    # Copy Each Row of Data
    for i, row in df.iterrows():
        for col in df:
            to_clipboard += str(row[col]) + """\t"""
        to_clipboard += """\r"""
    return pyperclip.copy(to_clipboard)

def pathlib_listdir(directory, reverse=False):
    """
    Function similar to os.listdir().  
    Returns a list of files from the input directory.  
    Designed for a pathlib.Path object.
    
    Uses utils.sort_list(unsorted_list, reverse=False) to sort the list.
    """
    directory = Path(directory)
    return sort_list([x.name for x in directory.glob('**/*') if x.is_file()], reverse=reverse)

def pathlib_glob(directory, glob_phrase, files=False, reverse=False):
    """
    Function similar to glob.glob() or Path.glob(directory)
    Returns a list of paths from the input.
    Designed for pathlib.Path object to return a list
    rather than pathlib.Path generator.
    Uses utils.sort_list(unsorted_list, reverse=False) to sort the paths
    Parameters: 
        files: False: returns the full path of each file.  If True, returns only file names.
    """
    directory = Path(directory)
    if files == False:
        the_files =  sort_list(
            [str(path) for path in directory.glob(glob_phrase) if path.is_file()], 
            reverse=reverse
        )
    else:
        the_files =  sort_list(
            [path.name for path in directory.glob(glob_phrase) if path.is_file()], 
            reverse=reverse
        )
    return the_files