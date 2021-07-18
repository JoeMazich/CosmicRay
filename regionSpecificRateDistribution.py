import geopy as gp
import numpy as np
import math
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from datetime import *
from taTools import *

from IPython.display import HTML
#animation.rcParams["animation.writer"] = "ffmpeg"


#                             TODO
#
# Merge functions
# split2regions returns the Center_Horz and Center_Vert to display
# debugs for RateCutoff
# comments on what the outputs of each main function should look like
# More comments at the bottom of the code

#                             HINTS
#
# there is a lot that can be optimized, changed, and made clearer, so please dig in as much as you can to make it as easy to understand and as fast as possible
# right now, it looks like the Lv0 method is the limiting factor for speed (given reasonable configs and choices) so if you can speed that method up, be my guest
# If I ever reference a "simple" time or "simple" date, I am referencing times and dates in the HHMMSS or YYMMDD format
# The FindRates method assumes a point every 10 mins, it is NOT dynamic
# Detector numbers are always strings (except in the NearDets method)
# Lv0rates are always floats
# Dates and times are, unsurprisingly, always datetimes (other than the obvious excpetions with simple dates and simple times for inputs and conversions etc.)
#
# The L0L1_dict looks like:
#     VVV    KEY     VVV              VVV    VALUE    VVV
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty], Rate, Rate Cutoff]
#
# The NLDN_dict looks like:
#   VVV  KEY  VVV      VVV   VALUE   VVV
#  [(Cartx, Carty)] = [time, peak current, C or G]
#
#
# L0L1 data format:                 NLDN data format:
# Column 0 | date                   Column 0 | date
# Column 1 | time                   Column 1 | time
# Column 2 | detector number        Column 2 | latitude
# Column 3 | level 0 rate           Column 3 | longitude
# Column 4 | level 1 rate           Column 4 | peak current
# Column 5 | dont use flag          Column 5 | type of lighting (C or G)
# Column 6 | warning flag
# Column 7 | quality
#
#
#


ONED_RATE_CUTOFF = .5 # the cut off for rates taken into account for the 1D plots (inclusive cutoff, meaning if this is at .5, rates at and below .5 are NOT counted for the one D plots)
ONED_CLOSEDETS_CUTOFF = 6 # the amount of dets that need to be above the ^ Cutoff around a 5x5 of a DET to count the DET in the 1D plots
TIME_NLDN_IS_ON = timedelta(minutes=20) # this is the amount of time NLDN data will stay on the TASD plot once it pops up (inclusive) (also, add ten mins to get that acutal amount of time it stay up)
RATE_WARNING = 3 # warn the user about rates above this amount

TAKE_OUT_DONTUSE = True
TAKE_OUT_WARN = True

ANI_SPEED = 900  #animation speed - lower is faster

# Decent colors to choose from : # ['#fc00b6', '#8e0da8', '#5201fe', '#0021ff', '#00f7f7', '#046b05', '#13f000', '#cf7600', '#731f00', '#b60909', '#8a0000', '#530028']

CMAP_COLORS = ['purple', 'blue', 'cyan', 'green', 'orange', 'red', 'maroon'] # set the colors for the 2D map
CMAP_BOUNDS = [-3, -2, -1, -0.5, 0.5, 1, 2, 3] # set the bounds for the colors on the 2D map [-5, -3, -1, -0.5, 0.5, 1, 3, 5]
# (Note that if you add any more beyond -5 and 5, you have to change vmin, vmax at sp_sensor_readings definition) (you can make this dynamic with CMAP_BOUNDS[0], CMAP_BOUNDS[len(CMAP_BOUNDS) - 1])

CMAP_COLORS_TEMP = ['#fc00b6', '#8e0da8', '#0021ff', 'cyan', 'green', 'orange', 'red', '#b60909', '#530028']
CMAP_BOUNDS_TEMP = [-30, -5, -3, -1, -0.5, 0.5, 1, 3, 5, 30] # set the bounds for the colors on the 2D map [-5, -3, -1, -0.5, 0.5, 1, 3, 5]


# Constants, i.e. dont change even if you think you don't need them anymore or replaced them in a function with another constant
TEN_MINS = timedelta(minutes=10)
TWO_HOURS = timedelta(hours=2)
THREE_HOURS = timedelta(hours=3)
SIX_HOURS = timedelta(hours=6)
# some basic init just to make things at the plot generation level (way down at the bottome of the code) a little easier
tasdnum,tasdx,tasdy,tasdz =[],[],[],[]
tasdxyz(tasdnum,tasdx,tasdy,tasdz)

# change time that looks like 123456 to a datetime.time that looks like 12:34:56
def Time_P2D(plain_time):
    hour = int(plain_time[0:2])
    min = int(plain_time[2:4])
    sec = int(plain_time[4:6])
    return time(hour, min, sec)

# change time that looks like 12:34:56 to a datetime.time that looks like 12:34:56
# (ok yes it looks the same, but it is a datetime.time object, trust me)
def Time_C2D(colon_time):
    temp = colon_time.split(":")
    hour = int(temp[0])
    min = int(temp[1])
    temp2 = temp[2].split(".")
    sec = int(temp2[0])
    microsec = int(temp2[1][0:6])
    return time(hour, min, sec, microsec)

# change a date that looks like 180322 to a datetime.date that looks like 2018-03-22
def Date_P2D(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return date(year, month, day)

# change a date like this: 2018-03-22 to a datetime.date
def Date_D2D(dashed_date):
    temp = dashed_date.split("-")
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    return date(year, month, day)

# this function takes in a det and returns a dict of dets near by it, im doing this by using the labeling of the dets:
# for example, to go up one det, you add one to the det num
# important nots about this is that it will return top leftmost det move right to the top rightmost, then go down
# one and return that row, etc, till the bottom rightmost
# additionally, if you do not center it (set centered to false) the det you input will be the top rightmost
# last thing is that, for even sizes (2, 4, 6, 8, etc) the "center" det will be follow the general idea
# [ ] [ ] [ ] [ ]  <<<
# [ ] [O] [X] [ ]  <<<  The dets iwht X's and O's are the "center" dets in this 4x4
# [ ] [X] [X] [ ]  <<<  but the one with the O is the center det (given that "centered" is true and it is not going based off the top leftmost)
# [ ] [ ] [ ] [ ]  <<<
#
# Oh yeah, almost forgot the GEM of this function: it will output a dict (of course) where the key is the relative coordinates and the value is the det num
# for instance, look at the 4x4 above. Say that the top, leftmost det num is 1317, the output dict will have (0,0): 1317 as an item.
# this also means it will have (0,3): 1617 as an item (1617 is three dets to the right of 1317, (0,0) -> (0,3) )
# this is very useful for when you want to iterate through all of these dets in a controlled fashion:
# rather than just "for det in dict.values()" (which you tatally can do if you don't care about relativve position)
# you can do a nested for loop, something like "for n for m in dict.keys" which allows you to pull the det num AND know the relative placement
# of that det compared to the other dets in the dict (I use this properity in the Create1DPlots method if you want to see an example)
def NearDets(det_num, size, centered):
    det_num = int(det_num)
    dict = {}

    # this is moving the det to the top leftmost section if it was given as a centered det
    if centered:
        l = math.floor((size/2) - .5)
        for i in range(l):
            det_num -= 99

    for n in range(size):
        temp_det_num = det_num
        for m in range(size):
            dict[(n, m)] = str(temp_det_num).rjust(4, "0")
            temp_det_num += 100
        det_num -= 1
    return dict

# this is, ehhhh
# the general idea for this function is to split up the dets into 4 seperate regions
# I use this to get the regions I need for the avging methods (you will see that after I call this down below, I append NW and NE to one N region, making the three regions)
# its not very dynamic, essentially one step away from just hardcoding the list of dets for each region in, but better that just doing that
# I am not going to comment much else on this one, I feel like its fairly easy to follow and besides, isn't the best it could be
# feel free to edit this (of course) based off of how you want to interact with the regions (you could make this function a relative of the NearDets function and use something similar to the current Create1DPlots method, for instance)
def Split2Regions():
    NW, NE, SE, SW = [], [], [], []
    top_left, top_right, bottom_right = "1218", "1318", "1317"

    file = open('tasd_gpscoors.txt', 'r')

    for line in file:
        columns = line.split()

        if columns[0] == top_left:
            top_left = (columns[1], columns[2])
        if columns[0] == top_right:
            top_right = (columns[1], columns[2])
        if columns[0] == bottom_right:
            bottom_right = (columns[1], columns[2])

    file.close()

    Center_Horz = (float(top_right[1]) + float(bottom_right[1])) / 2
    Center_Vert = (float(top_right[0]) + float(top_left[0])) / 2 - .005 # this - .005 is a slight adjustment as det 0618 ended up in the SW when it should be in the N

    file = open("tasd_gpscoors.txt",'r')

    for line in file:
        columns = line.split()

        if (float(columns[1]) > Center_Vert and float(columns[2]) < Center_Horz):
            NW.append(columns[0])
        if (float(columns[1]) > Center_Vert and float(columns[2]) > Center_Horz):
            NE.append(columns[0])
        if (float(columns[1]) < Center_Vert and float(columns[2]) < Center_Horz):
            SW.append(columns[0])
        if (float(columns[1]) < Center_Vert and float(columns[2]) > Center_Horz):
            SE.append(columns[0])
    file.close()
    return NW, NE, SW, SE

# returns a time table ranging from 00:00:00 to 23:50:00 for use in comparisons
# due to annoying requirments of datetime object, needs a date passed through, in this case a
# date formatted like 180322 (str) is needed, therefore pass through the input date
# so the comparisons are not days off
def Time_Table(date):
    time_table = []
    dateAndTime = datetime.combine(Date_P2D(date), time(hour=0, minute=0, second=0))
    time_table.append(dateAndTime)
    for i in range(143):
        dateAndTime += TEN_MINS
        time_table.append(dateAndTime)
    return time_table

# Change latitude and longitude to cart cooridinates
def LL2CCoors(LL_tuple):
    # create a gps point
    gps = gp.point.Point(LL_tuple[0], LL_tuple[1], 0)
    # convert it into cart x, y, z
    x, y, z = gps2cart(gps)
    # we only care about x and y
    return (x, y)

# find the Cart coordinates given a detector number
def Det2Cart(det_num):
    file = open('tasd_gpscoors.txt', 'r')
    # we have to look through tasd_gpscoors and match the det num to get its lat long
    for line in file:
        columns = line.split()

        if det_num == columns[0]:
            # once we math it, we convert lat long to x, y, z, and we only care about x, y
            gps = gp.point.Point(columns[1], columns[2], 0)#columns[3])
            x, y, z = gps2cart(gps)
            return (x, y)
    file.close()
    # if for some reason we never found the det, we will
    raise Exception("Det2Cart missed " + det_num)
    return (None, None)

# given a properly formatted dict of lv0rates, times, and det numbers, (recieved from the L0L1 funcction, look at comments about that function)
# this will append the proper rates (or lack thereof) onto the dict
# This will change the dict to look like the following:
#     VVV    KEY     VVV              VVV    VALUE    VVV
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty], Rate, Rate Cutoff]
def FindRates(dict, this_time, this_date):
    excess_array, deficit_array, neutral_array = [], [], []
    this_time = datetime.combine(Date_P2D(this_date), (Time_P2D(this_time)))

    previous_time = this_time - TEN_MINS

    for time_det, lv0_latlong in dict.items():
        if this_time == time_det[0]:
            this_lv0 = lv0_latlong[0]
            if (previous_time, time_det[1]) in dict.keys():
                previous_lv0 = dict[previous_time, time_det[1]][0]
                rate = ((this_lv0 - previous_lv0) / previous_lv0) * 100
                if rate > -40:
                    if rate < -0.5:
                        deficit_array.append(rate)
                    elif rate > 0.5:
                        excess_array.append(rate)
                    else:
                        neutral_array.append(rate)

    return excess_array, deficit_array, neutral_array

def FindTempDiffs(dict):

    for time_det, temp_latlong in dict.items():
        this_temp = temp_latlong[0]
        this_det = time_det[1]
        this_time = time_det[0]
        next_time = this_time + TEN_MINS
        previous_time = this_time - TEN_MINS

        if (previous_time, this_det) in dict.keys():
            previous_temp = dict[previous_time, this_det][0]
            abs_change = this_temp - previous_temp
            temp_latlong.append(abs_change)
        else:
            temp_latlong.extend([0])



# given a filename (most likely a date in the 180322 format) this will read the data for L0L1 and, according to
# the flags, will return a dict in the following format:
#     VVV    KEY     VVV           VVV    VALUE    VVV
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty]]
def Lv0(filename):
    debug_count = 0
    time_det_lv0rate_CCoors, time_det_temp_CCoors = {}, {}
    file = open("DataDates/" + filename + "/L0L1.txt", 'r')

    for line in file:
        columns = line.split()
        if not TAKE_OUT_DONTUSE or float(columns[5]) == 0:
            if not TAKE_OUT_WARN or int(columns[6]) == 0:
                time_det_lv0rate_CCoors[datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))), columns[2]] = [float(columns[3]), Det2Cart(columns[2])]
                time_det_temp_CCoors[datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))), columns[2]] = [float(columns[8]), Det2Cart(columns[2])]
                debug_count += 1
    file.close()

    print("Found " + str(debug_count) + " data points *")

    return time_det_lv0rate_CCoors, time_det_temp_CCoors


def MakePlots(this_date, this_time, excess):

    print("\nGrabbing L0L1 data...")
    L0L1_dict, Temp_dict = Lv0(this_date)
    print("\nFinding rates of change...")
    excess_array, deficit_array, neutral_array = FindRates(L0L1_dict, this_time, this_date)

    if excess:
        neutral_array = np.asarray(deficit_array + neutral_array)
        intrest_array = np.asarray(excess_array)
        label = 'Excess'
    else:
        neutral_array = np.asarray(excess_array + neutral_array)
        intrest_array = np.asarray(deficit_array)
        label = 'Deficit'

    neutral_mean = np.mean(neutral_array)
    intrest_mean = np.mean(intrest_array)

    neutral_rms = np.sqrt(np.mean(neutral_array**2))
    intrest_rms = np.sqrt(np.mean(intrest_array**2))

    plt.rc('xtick', labelsize = 6)
    plt.rc('ytick', labelsize = 6)
    plt.xlabel('Rates')
    plt.ylabel('Number of Events')
    plt.plot([neutral_mean]*2, [0, 16], label='Neutral mean')
    plt.plot([neutral_rms]*2, [0, 16], label='Neutral rms')
    plt.plot([intrest_mean]*2, [0, 16], label=label+' mean')
    plt.plot([intrest_rms]*2, [0, 16], label=label+' rms')
    plt.hist(neutral_array, bins=50, histtype='step', label='Neutral')
    plt.hist(intrest_array, bins=50, histtype='step', label=label)
    plt.semilogy()
    plt.legend()
    plt.title(Time_P2D(this_time))
    plt.show()


if __name__ == "__main__":

    input_date = input("\nWhich date? ")
    input_time = input("What time? ")
    excess = int(input("Excess (1) or deficit (0)? "))

    MakePlots(input_date, input_time, excess)
