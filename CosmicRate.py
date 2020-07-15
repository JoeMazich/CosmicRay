import geopy as gp
import numpy as np

import matplotlib.colors as mcolors #check if i need this
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from datetime import *
from taTools import *

from IPython.display import HTML
animation.rcParams["animation.writer"] = "ffmpeg"


#                             TODO
#
# Create N, SW, and SE axies
# Create time counters for N, SW, and SE axies
# Create automated rules for splitting the dets into regions
# Find a way to apply cutoffs (geometrical and value-wise) to rates for 1D plots, maybe in FindRates method
#       maybe add another item to the value list, '''either a flag for if the rate is above .5''' or the rate itself if it is above .5
#       then have another extraction function look at the flags? Check statments like: if (.2)   (is .7 true or false? if true for everything but 0, could use the second method as described above)
# Create simple debuging #s
#

# IDEA:
#
# I like the 1 and 0 flag idea: have a function the loops through the N region, if a det flag is 1, find surrounding dets
# Add up all the 1 and 0s from surrounding dets, if the addition passes a certain amount, add the det rate to a running avg
# append final avg to a list (gonna have to pass through the time table, ugh, so only call it once and name it a variable)
# return that list
#

#                             HINTS
#
# If I ever reference a "simple" time or "simple" date, I am referencing times and dates in the ###### format
# The FindRates method assumes a point every 10 mins
# Detector numbers are always strings (except in the NearDets method)
# Lv0rates are always floats
# Times are, unsurprisingly, always datetimes (other than the obvious excpetions with simple dates and simple times)
#
# The L0L1_dict looks like:
#     VVV    KEY     VVV              VVV    VALUE    VVV
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty], Rate]
#
# The NLDN_dict looks like:
#   VVV  KEY  VVV      VVV   VALUE   VVV
#  [(Cartx, Carty)] = [time, peak current]
#
# L0L1 data format:                 NLDN data format:
# Column 0 | date                   Column 0 | date
# Column 1 | time                   Column 1 | time
# Column 2 | detector number        Column 2 | latitude
# Column 3 | level 0 rate           Column 3 | longitude
# Column 4 | level 1 rate           Column 4 | peak current
# Column 5 | dont use flag          Column 5 | type of lighting
# Column 6 | warning flag
# Column 7 | quality
#
#
#


ONED_RATE_CUTOFF = .5 # the cut off for rates taken into account for the 1D plots (inclusive cutoff, meaning if this is at .5, rates at and below .5 are NOT counted for the one D plots)
ONED_CLOSEDETS_CUTOFF = 0 # the amount of dets that need to be above the ^ Cutoff around a 5x5 of a DET to count the DET in the 1D plots
TIME_NLDN_IS_ON = timedelta(minutes=50) # this is the amount of time NLDN data will stay on the TASD plot once it pops up (inclusive) (also, add ten mins to get that acutal amount of time it stay up)

TAKE_OUT_DONTUSE = True
TAKE_OUT_WARN = True

ANI_SPEED = 500  #animation speed - lower is faster

CMAP_COLORS = ["blue", "#00FFFF", "green", "#FFa500", "red"] # set the colors for the 2D map
CMAP_BOUNDS = [-3, -1, -.5, .5, 1, 3] # set the bounds for the colors on the 2D map



TEN_MINS = timedelta(minutes=10)

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
    return time(hour, min, sec)

# change a date that looks like 180322 to a datetime.date that looks like 2018-03-22
def Date_P2D(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return date(year, month, day)

def Date_D2D(dashed_date):
    temp = dashed_date.split("-")
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    return date(year, month, day)

# returns a time table ranging from 00:00:00 to 23:50:00 for use in comparisons
# due to annoying requirments of datetime object, needs a date passed through, in this case a
# date formatted like 180322 (str) is needed, therefore pass through the date that is being looked at
# so the comparisons in the ExtractL0rates function are correct
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
            gps = gp.point.Point(columns[1], columns[2], columns[3])
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
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty], Rate]
def FindRates(dict):
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
        else:
            #if not, append None to this time as a place holder
            lv0_latlong.append(0)

# given a filename (most likely a date in the 180322 format) this will read the data for L0L1 and, according to
# the flags, will return a dict in the following format:
#     VVV    KEY     VVV           VVV    VALUE    VVV
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty]]
def L0L1(filename):
    time_det_lv0rate_CCoors = {}
    file = open("DataDates/" + filename + "/L0L1.txt", 'r')

    for line in file:
        columns = line.split()
        if not TAKE_OUT_DONTUSE or int(columns[5]) == 0:
            if not TAKE_OUT_WARN or int(columns[6]) == 0:
                time_det_lv0rate_CCoors[datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))), columns[2]] = [float(columns[3]), Det2Cart(columns[2])]
    file.close()

    return time_det_lv0rate_CCoors

# given a filename (most likely a date in the 180322 format) this will read the data for NLDN
def NLDN(filename):
    CCoors_time_PCurrent = {}
    times, Peak_Currents = [], []
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
        CCoors_time_PCurrent[LL2CCoors((columns[2], columns[3]))] = (time, float(columns[4]))

        times.append(time)
        Peak_Currents.append(float(columns[4]))
    return CCoors_time_PCurrent, times, Peak_Currents

# this will take out the necessary data from the L0 rate dict, it will return two arrays, one for placement and one for rates (color)
def ExtractL0rates(dict, time_table):
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
        # append each frame to the ulitmate arrays
        detectors_placements.append(frame_detectors_placements)
        detectors_rates.append(frame_detectors_rates)
        # reset the frames
        frame_detectors_placements, frame_detectors_rates = [], []

    return detectors_placements, detectors_rates

# this extracts the important data for NLDN, it is not optimized very well, so if you want and you fully understand what it is doing, take a shot at making it faster
def ExtractNLDN(dict, time_table):
    # this flag is used  to tell if there is no data for a frame of the NLDN data that appears on the TASD plot
    # if there is no data, this flag stays false and the array is appened with (None, None) to preserve the structure of the array
    # so that the .set_offsets function is happy that it sees a tuple of None rather than just nothing
    flag = False
    # the ULTIMATE array that will be passed through to the plots
    NLDNonTASD = []
    # a frame array similar to those in ExtractL0rates
    frame_NLDNonTASD = []
    # this is for grabbing time vs peak current for the NLDN plot
    # this is for grabbing each frame of the NLDN data that appears on the TASD array, note that the NLDN data will dissappear
    for table_time in time_table:
        for CCoor, time_PCurrent in dict.items():
            if time_PCurrent[0] <= (table_time + TEN_MINS) and time_PCurrent[0] >= (table_time - TIME_NLDN_IS_ON):
                frame_NLDNonTASD.append(CCoor)
                flag = True
        if not flag:
            frame_NLDNonTASD.append((None, None))
        flag = False

        NLDNonTASD.append(frame_NLDNonTASD)
        frame_NLDNonTASD = []

    return NLDNonTASD

# init function for the animation
def init():
    lp_NLDN_time_counter.set_data([], [])
    return list_plots

# update function, the bread and butter for the animation function
def update(frame):

    x = datetime.combine(Date_P2D(this_date), time(second=0)) + (frame * TEN_MINS)
    y = np.linspace(-300, 1000, 250)

    # update the positions of the readings for TASD
    sp_sensor_readings.set_offsets(detectors_placements[frame])
    # update the TASD colors based off of rates, note that the function call for this is .set_array because why not and it needs
    # a numpy array, because why not
    sp_sensor_readings.set_array(np.asarray(detectors_rates[frame]))
    sp_lightning_readings.set_offsets(NLDNonTASD[frame])
    lp_NLDN_time_counter.set_data(x, y)
    return list_plots

if __name__ == '__main__':

    this_date = input("Which date? ")
    TimeTable = Time_Table(this_date)

    print("Grabbing L0L1 data...")
    L0L1_dict = L0L1(this_date)
    print("Finding rates of change...")
    FindRates(L0L1_dict)
    print("Extracting data...")
    detectors_placements, detectors_rates = ExtractL0rates(L0L1_dict, TimeTable)

    print("Grabbing NLDN data...")
    NLDN_dict, PC_Times, Peak_Currents = NLDN(this_date)
    print("Extracting data...")
    NLDNonTASD = ExtractNLDN(NLDN_dict, TimeTable)

    fig = plt.figure(constrained_layout=False)

    cmap = mpl.colors.ListedColormap(CMAP_COLORS)
    norm = mpl.colors.BoundaryNorm(CMAP_BOUNDS, cmap.N)

    gs_left = fig.add_gridspec(5, 3, left=0.08, right=0.48, top=.92, bottom=.08, wspace=1, hspace=0.5)
    gs_right = fig.add_gridspec(2, 4, left=0.53, right=0.98, wspace=0.6, hspace=0.3)


    TASDax = fig.add_subplot(gs_left[:3, :3])
    TASDax.set_xlim(-20, 20)
    TASDax.set_ylim(-23, 18)
    sp_sensors = TASDax.scatter(tasdx, tasdy, c='yellow', s=7, marker='.')
    sp_sensor_readings = TASDax.scatter([], [], c=[], s=7, cmap=cmap, norm=norm, marker='s', vmin = -1, vmax = 1)
    sp_lightning_readings = TASDax.scatter([], [], c='purple', s=7, marker='+')
    plt.colorbar(sp_sensor_readings, cmap=cmap, norm=norm)

    NLDNax = fig.add_subplot(gs_left[3:, :3])
    NLDNax.grid(True)
    NLDNax.set_xlim(datetime.combine(Date_P2D(this_date), (time(second=0))), datetime.combine(Date_P2D(this_date), (time(hour=23, minute=59))))
    NLDNax.set_ylim(-250, 250)
    NLDNax.set_xlabel("Time")
    NLDNax.set_ylabel("Peak Current")
    sp_lightning_level = NLDNax.scatter(PC_Times, Peak_Currents, c='purple', s=7, marker='+')
    lp_NLDN_time_counter, = NLDNax.plot([], [], lw=1, c='blue')

    list_plots = [sp_sensor_readings, sp_lightning_readings, lp_NLDN_time_counter]

    anim = animation.FuncAnimation(fig, update, init_func=init, interval=ANI_SPEED, blit=True, repeat=True, frames=144)

    plt.show()
