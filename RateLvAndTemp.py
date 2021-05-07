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
TIME_NLDN_IS_ON = timedelta(hours=1, minutes=30) # this is the amount of time NLDN data will stay on the TASD plot once it pops up (inclusive) (also, add ten mins to get that acutal amount of time it stay up)
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
def FindRates(dict):
    rate_warns = []
    debug_count, debug_count2 = 0, 0
    for time_det, lv0_latlong in dict.items():
        # get all necessary info
        this_lv0 = lv0_latlong[0]
        this_det = time_det[1]
        this_time = time_det[0]
        next_time = time_det[0] + TEN_MINS
        # check to see if the same det exsists ten mins after in the dict
        if (next_time, this_det) in dict.keys():
            # if it is, then find the rate of change and append it to the list (the value of the dict)
            # at this_time (not at next_time)
            # VV This VV exsists here because we had to check it exsisted first
            next_lv0 = dict[next_time, this_det][0]
            rate = ((next_lv0 - this_lv0) / this_lv0) * 100
            lv0_latlong.append(rate)
            # this if else is used for the rate cutoff and it will be used in the 1D plots
            if abs(rate) >= ONED_RATE_CUTOFF:
                lv0_latlong.append(1)
            else:
                lv0_latlong.append(0)

            if abs(rate) >= RATE_WARNING:
                rate_warns.append((this_det, this_time))

            debug_count += 1
        else:
            #if not, append 0, 0 to this time as a place holder (one for rate the other for rate cutoff)
            lv0_latlong.extend([0, 0])
            debug_count2 += 1
    print("Found " + str(debug_count) + " rates")
    print("Found " + str(debug_count2) + " points without a second hit")
    print("Total is " + str(debug_count + debug_count2) + " rates *")

    return rate_warns

def FindTempDiffs(dict):

    for time_det, temp_latlong in dict.items():
        this_temp = temp_latlong[0]
        this_det = time_det[1]
        this_time = time_det[0]
        next_time = this_time + TEN_MINS

        if (next_time, this_det) in dict.keys():
            next_temp = dict[next_time, this_det][0]
            abs_change = next_temp - this_temp
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
    file = open("DataDates/temp/" + filename + "/L0L1.txt", 'r')

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

# given a filename (most likely a date in the 180322 format) this will read the data for NLDN
def NLDN(filename):
    debug_count = 0
    CCoors_time_PCurrent = {}
    C_times, C_Peak_Currents, G_times, G_Peak_Currents = [], [], [], []

    file = open("DataDates/" + filename + "/NLDN.txt", 'r')
    # the reason this one looks fairly different when compared to the L0L1 function is because a dict is still made, but
    # times and Peak_Currents just pulls the data into seperate lists. This is done because it would have to otherwise be extracted from
    # the dict again, meaning this is faster and slightly easier, albeit a bit more confusing
    # also just to make it worse, I decided to make this dict keys be the Cart coordinates, unlike the L0L1 dict (where time and det # is the key)
    # this was done because, for some reason, python does not like datetimes as the sole key, it does not like iterating through them, but tuples
    # that contain a datetime are fine because they act as a wrapper, as is the case in L0L1 dict
    for line in file:
        columns = line.split()
        time = datetime.combine(Date_D2D(columns[0]), (Time_C2D(columns[1])))

        if columns[5] == "C":
            C_times.append(time)
            C_Peak_Currents.append(float(columns[4]))
            CCoors_time_PCurrent[LL2CCoors((columns[2], columns[3]))] = (time, float(columns[4]), "C")

        if columns[5] == "G":
            G_times.append(time)
            G_Peak_Currents.append(float(columns[4]))
            CCoors_time_PCurrent[LL2CCoors((columns[2], columns[3]))] = (time, float(columns[4]), "G")

        debug_count += 1

    print("Found " + str(debug_count) + " data points")
    return CCoors_time_PCurrent, C_times, C_Peak_Currents, G_times, G_Peak_Currents

# this will take out the necessary data from the L0 rate dict, it will return two arrays, one for placement and one for rates (color)
def ExtractL0rates(dict, time_table):
    debug_count = 0
    # these are the ULTIMATE arrays, only small tweaks will be needed later on to have the animation function read them properly
    detectors_placements, detectors_rates = [], []
    # these are temp arrays that are created to get the information for a frame, then are appeneded to the ULITMATE arrays above
    frame_detectors_placements, frame_detectors_rates = [], []
    # if a cutoff is needed for time, to look at a more specifc window, it can be done here
    # (Or in the Time_Table function but its best to leave that as is and do it here)
    for table_time in time_table:
        for time_det, lv0_ccoors_rate in dict.items():
            # this is totally overboard for what is needed for this function (we only need this_time (to check), this_ccoors (for placement), and this_rate (for the colors))
            # butthis serves as a good example of how this dict setup can be use if it is desired to be used differently later
            this_time = time_det[0]
            this_det = time_det[1]
            this_lv0 = lv0_ccoors_rate[0]
            this_ccoor = lv0_ccoors_rate[1]
            this_rate = lv0_ccoors_rate[2]
            # grab all the info for each time, making each time a frame
            if this_time == table_time:
                frame_detectors_placements.append(this_ccoor)
                frame_detectors_rates.append(this_rate)
                debug_count += 1
        # append each frame to the ulitmate arrays
        detectors_placements.append(frame_detectors_placements)
        detectors_rates.append(frame_detectors_rates)
        # reset the frames
        frame_detectors_placements, frame_detectors_rates = [], []
    print("Found " + str(debug_count) + " extraction matches *")
    return detectors_placements, detectors_rates

# this extracts the important data for NLDN, it is not optimized very well, so if you want and you fully understand what it is doing, take a shot at making it faster
def ExtractNLDN(dict, time_table):
    debug_count, debug_count2 = 0, 0
    # this flag is used  to tell if there is no data for a frame of the NLDN data that appears on the TASD plot
    # if there is no data, this flag stays false and the array is appened with (None, None) to preserve the structure of the array
    # so that the .set_offsets function is happy that it sees a tuple of None rather than just nothing
    C_flag, G_flag = False, False
    # the ULTIMATE array that will be passed through to the plots
    C_NLDNonTASD, G_NLDNonTASD = [], []
    # a frame array similar to those in ExtractL0rates
    C_frame_NLDNonTASD, G_frame_NLDNonTASD = [], []
    # this is for grabbing time vs peak current for the NLDN plot
    # this is for grabbing each frame of the NLDN data that appears on the TASD array, note that the NLDN data will dissappear
    for table_time in time_table:
        for CCoor, time_PCurrent_CG in dict.items():
            if time_PCurrent_CG[0] <= (table_time + TEN_MINS) and time_PCurrent_CG[0] >= (table_time - TIME_NLDN_IS_ON):
                if time_PCurrent_CG[2] == "C":
                    C_frame_NLDNonTASD.append(CCoor)
                    C_flag = True
                if time_PCurrent_CG[2] == "G":
                    G_frame_NLDNonTASD.append(CCoor)
                    G_flag = True
                debug_count += 1
        if not C_flag:
            C_frame_NLDNonTASD.append((None, None))
            debug_count2 += 1
        if not G_flag:
            G_frame_NLDNonTASD.append((None, None))
            debug_count2 += 1
        C_flag = False
        G_flag = False

        C_NLDNonTASD.append(C_frame_NLDNonTASD)
        C_frame_NLDNonTASD = []
        G_NLDNonTASD.append(G_frame_NLDNonTASD)
        G_frame_NLDNonTASD = []
    print("Found " + str(debug_count) + " extraction matches")
    print("Found " + str(debug_count2) + " extraction misses")
    print("Total is " + str(debug_count + debug_count2) + " extractions")
    return C_NLDNonTASD, G_NLDNonTASD

def MakePlots(this_date, save):

    # Stright forward, make a gridspec of appropiate size, and iterate through each plot like (0,0), (0,1), ... , (1,0), ...
    # and create them as it goes

    # update function, the bread and butter for the animation function
    def update(frame):

        # find the points to place the blue line of ALL plots that have blue lines for each frame
        x = datetime.combine(Date_P2D(this_date), time(second=0)) + (frame * TEN_MINS)
        y = np.linspace(-300, 300)

        # update the positions of the readings for TASD
        sp_sensor_readings.set_offsets(detectors_placements[frame])
        # update the TASD colors based off of rates, note that the function call for this is .set_array because why not and it needs
        # a numpy array, because why not
        sp_sensor_readings.set_array(np.asarray(detectors_rates[frame]))

        sp_G_lightning_readings.set_offsets(G_NLDNonTASD[frame])
        sp_C_lightning_readings.set_offsets(C_NLDNonTASD[frame])

        sp_temp_sensor_readings.set_offsets(temp_det_placements[frame])
        sp_temp_sensor_readings.set_array(np.asarray(temp_det_diffs[frame]))

        sp_temp_G_lightning_readings.set_offsets(G_NLDNonTASD[frame])
        sp_temp_C_lightning_readings.set_offsets(C_NLDNonTASD[frame])

        lp_NLDN_time_counter.set_data(x, y)

        return list_plots

    print("Make sure all of the *'s are the same number")
    # some useful constants
    TimeTable = Time_Table(this_date)
    ZeroHour = datetime.combine(Date_P2D(this_date), (time(second=0)))
    LastHour = datetime.combine(Date_P2D(this_date), (time(hour=23, minute=59)))
    # for regional avging
    NW_dets, NE_dets, SW_dets, SE_dets = Split2Regions()
    N_dets = NW_dets + NE_dets
    # for lv0 1D stuff
    Size_of_OneD = 4
    Centered_Det = "0308"

    # getting the Lv0 stuff
    print("\nGrabbing L0L1 data...")
    L0L1_dict, Temp_dict = Lv0(this_date)
    print("\nFinding rates of change...")
    rate_warns = FindRates(L0L1_dict)
    FindTempDiffs(Temp_dict)
    print("\nExtracting L0L1 data...")
    detectors_placements, detectors_rates = ExtractL0rates(L0L1_dict, TimeTable)
    temp_det_placements, temp_det_diffs = ExtractL0rates(Temp_dict, TimeTable)
    # getting the NLDN stuff
    print("\nGrabbing NLDN data...")
    NLDN_dict, C_Times, C_Peak_Currents, G_Times, G_Peak_Currents = NLDN(this_date)
    print("\nExtracting NLDN data...")
    C_NLDNonTASD, G_NLDNonTASD = ExtractNLDN(NLDN_dict, TimeTable)

    # Make labels for the plots
    xLabels_NLDN, xLabels_OneD  = [], []
    for i in range(13):
        xLabels_NLDN.append(ZeroHour + i * TWO_HOURS)

    # all this stuff below here is plot creation stuff
    # a bunch of it consists of tiny tweaks to make the plots look better and more readable
    # most all of it is pretty self explanitory
    fig = plt.figure(constrained_layout=False)
    fig.suptitle(this_date, fontsize=10)

    # annotation specs (for the 1D plots)
    anno_opts = dict(xy=(0.5, 0.9), xycoords='axes fraction', va='center', ha='center')

    # color map stuff (for the TASD)
    cmap = mpl.colors.ListedColormap(CMAP_COLORS)
    norm = mpl.colors.BoundaryNorm(CMAP_BOUNDS, cmap.N)

    # cmap for temp stuff
    cmap_Temp = mpl.colors.ListedColormap(CMAP_COLORS_TEMP)
    norm_Temp = mpl.colors.BoundaryNorm(CMAP_BOUNDS_TEMP, cmap_Temp.N)

    # the left grid spec, the right one has to be defined by the Create1DPlots method
    gs_left = fig.add_gridspec(5, 2, left=0.09, right=0.91, top=.87, bottom=0.09, wspace=0.1, hspace=0.5)

    # setting the x and y tick label sizes
    plt.rc('xtick', labelsize = 6)
    plt.rc('ytick', labelsize = 6)

    # creating the TASD plot (top left)
    TASDax = fig.add_subplot(gs_left[:3, 0])
    TASDax.title.set_text("Rate Change")
    TASDax.set_xlim(-20, 20)
    TASDax.set_ylim(-23, 18)
    sp_sensors = TASDax.scatter(tasdx, tasdy, c='yellow', s=7, marker='.')
    sp_sensor_readings = TASDax.scatter([], [], c=[], s=7, cmap=cmap, norm=norm, marker='s', vmin = -30, vmax = 30)
    sp_G_lightning_readings = TASDax.scatter([], [], c='.4', s=10, marker='+')
    sp_C_lightning_readings = TASDax.scatter([], [], c='black', s=10, marker='+')
    plt.colorbar(sp_sensor_readings)

    Tempax = fig.add_subplot(gs_left[:3, 1])
    Tempax.title.set_text("Temperature Change")
    Tempax.set_xlim(-20, 20)
    Tempax.set_ylim(-23, 18)
    Tempax.set_yticks([])
    sp_temp_sensors = Tempax.scatter(tasdx, tasdy, c='yellow', s=7, marker='.')
    sp_temp_sensor_readings = Tempax.scatter([], [], c=[], s=7, cmap=cmap_Temp, norm=norm_Temp, marker='s', vmin = -30, vmax = 30)
    sp_temp_G_lightning_readings = Tempax.scatter([], [], c='.4', s=10, marker='+')
    sp_temp_C_lightning_readings = Tempax.scatter([], [], c='black', s=10, marker='+')
    plt.colorbar(sp_temp_sensor_readings)

    NLDNax = fig.add_subplot(gs_left[3:, :])
    NLDNax.grid(True)
    NLDNax.set_xlim(ZeroHour, LastHour)
    NLDNax.set_ylim(-250, 250)
    NLDNax.set_xticks(xLabels_NLDN)
    NLDNax.set_xlabel("Time")
    NLDNax.set_ylabel("Peak Current")
    NLDNax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    sp_lightning_level = NLDNax.scatter(G_Times, G_Peak_Currents, c='.4', s=7, marker='+', label="G Events")
    sp_lightning_level = NLDNax.scatter(C_Times, C_Peak_Currents, c='black', s=7, marker='+', label="C Events")
    lp_NLDN_time_counter, = NLDNax.plot([], [], lw=1, c='blue')
    NLDNax.legend(prop={"size":5})

    # the update function for animation must return all of the updated plots
    list_plots = [sp_sensor_readings, sp_temp_sensor_readings, sp_G_lightning_readings, sp_C_lightning_readings, sp_temp_G_lightning_readings, sp_temp_C_lightning_readings, lp_NLDN_time_counter]

    # *THE* animation function, literally everything above this was sorted, parsed, appended, etc all for this one line function
    anim = animation.FuncAnimation(fig, update, interval=ANI_SPEED, blit=True, repeat=True, frames=144)

    # a sigle print statment so that the output looks nicer, but im guessing that you probably knew or guessed that
    print()
    # print out all of the warnings we tripped (currently, this is NOT dynamic and only prints out the above 5% warning (the only current warning) but provides a base for additional warnings later)
    for warning in rate_warns:
        print("Warning: " + warning[0] + " at " + warning[1].strftime("%H:%M:%S") + " is above " + str(RATE_WARNING) + "%")

    print()

    if (save):
        path = "Movies/" + str(this_date)
        name = "RateLv0"
        if not os.path.isdir(path):
            os.mkdir(path)
        print("Saving...")
        HTML(anim.to_html5_video())
        anim.save(path + "/" + name + ".mov", fps=1, writer="ffmpeg", dpi=1000, bitrate=5000)
        plt.close(fig)

    return anim


if __name__ == "__main__":

    input_date = input("\nWhich date? ")
    # check if date exists
    while not os.path.isdir("DataDates/" + input_date):
        input_date = input("No data for that date. Choose again, or n to stop: ")
        if input_date == "n":
            break
    if input_date is not "n":
        animation = MakePlots(input_date, False)

        plt.show()

        # saving the animation, note that the place variable and the name variable can be dynamic
        save = str(input("Save? [y/n] "))
        while (save != "y" and save != "n"):
            save = str(input("Invalid response. Save? [y/n] "))

        if (save == "y"):

            path = "Movies/temp/" + str(input_date)
            name = "TempandRate"

            if not os.path.isdir(path):
                os.mkdir(path)
            print("Saving...")
            HTML(animation.to_html5_video())
            animation.save(path + "/" + name + ".mov", fps=1, writer="ffmpeg", dpi=1000, bitrate=5000)

    else:
        print("Goodbye!")
