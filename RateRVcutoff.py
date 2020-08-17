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
# set __name__ == __main__ to a function call so I can just call this class somewhere else
# split2regions returns the Center_Horz and Center_Vert to display
# debugs for RateCutoff
# comments on what the outputs of each main function should look like
# More comments at the bottom of the code
# Dont need to set sp_lightning_level equal to .scatter, can just do .scatter

#                             IDEAS
#
# could have the cutoff look backwards in time by 10 min and in the future by 10 mins
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
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty], Rate, Rate Cutoff]
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
TIME_NLDN_IS_ON = timedelta(hours=1, minutes=30) # this is the amount of time NLDN data will stay on the TASD plot once it pops up (inclusive) (also, add ten mins to get that acutal amount of time it stay up)
RATE_WARNING = 5 # warn the user about rates above this amount

TAKE_OUT_DONTUSE = True
TAKE_OUT_WARN = True

ANI_SPEED = 750  #animation speed - lower is faster

CMAP_COLORS = ['purple', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red'] # set the colors for the 2D map
CMAP_BOUNDS = [-5, -3, -1, -0.5, 0.5, 1, 3, 5] # set the bounds for the colors on the 2D map
# (Note that if you add any more beyond -5 and 5, you have to change vmin, vmax at sp_sensor_readings definition)



TEN_MINS = timedelta(minutes=10)
THREE_HOURS = timedelta(hours=3)
SIX_HOURS = timedelta(hours=6)

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

# this function takes in a det and returns dets near by it. I am using the nice 2D ordering of the dets, but
# if you prefer to use a different geometric function, you can use that, just make sure it reutrns a list of strings of the names of dets
def NearDets(det_num):
    det_num = int(det_num)
    return [str(det_num - 99), str(det_num + 1), str(det_num + 101), str(det_num - 100), str(det_num + 100), str(det_num - 101), \
    str(det_num - 1), str(det_num + 99), str(det_num - 198), str(det_num - 98), str(det_num + 2), str(det_num + 102), str(det_num + 202), \
    str(det_num - 199), str(det_num + 201), str(det_num - 200), str(det_num + 200), str(det_num - 201), str(det_num + 199), str(det_num - 202),\
    str(det_num - 102), str(det_num - 2), str(det_num + 98), str(det_num + 198)]

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

# given a filename (most likely a date in the 180322 format) this will read the data for L0L1 and, according to
# the flags, will return a dict in the following format:
#     VVV    KEY     VVV           VVV    VALUE    VVV
#  [Datetime, Detector Number] = [Lv0rate, [Cartx, Carty]]
def L0L1(filename):
    debug_count = 0
    time_det_lv0rate_CCoors = {}
    file = open("DataDates/" + filename + "/L0L1.txt", 'r')

    for line in file:
        columns = line.split()
        if not TAKE_OUT_DONTUSE or int(columns[5]) == 0:
            if not TAKE_OUT_WARN or int(columns[6]) == 0:
                time_det_lv0rate_CCoors[datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))), columns[2]] = [float(columns[3]), Det2Cart(columns[2])]
                debug_count += 1
    file.close()

    print("Found " + str(debug_count) + " data points *")

    return time_det_lv0rate_CCoors

# given a filename (most likely a date in the 180322 format) this will read the data for NLDN
def NLDN(filename):
    debug_count = 0
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
        debug_count += 1
    print("Found " + str(debug_count) + " data points")
    return CCoors_time_PCurrent, times, Peak_Currents

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
                debug_count += 1
        if not flag:
            frame_NLDNonTASD.append((None, None))
            debug_count2 += 1
        flag = False

        NLDNonTASD.append(frame_NLDNonTASD)
        frame_NLDNonTASD = []
    print("Found " + str(debug_count) + " extraction matches")
    print("Found " + str(debug_count2) + " extraction misses")
    print("Total is " + str(debug_count + debug_count2) + " extractions")
    return NLDNonTASD

def RateCutoff(dict, region, time_table):
    avgs = []
    for table_time in time_table: # for each time
        total, hits = 0, 0 # start a running total
        for det in region: # for each det in the region
            if (table_time, det) in dict.keys(): # if it exists

                count = 0 # start a count
                for NearDet in NearDets(det):
                    if (table_time, NearDet) in dict.keys():
                        count += dict[table_time, NearDet][3] # and count how many near by dets make the cutoff

                if dict[table_time, det][3] and count >= ONED_CLOSEDETS_CUTOFF: # if enough neardets make the cut off and the det itself makes the cutoff
                    total += dict[table_time, det][2] # add the rate to the total
                    hits += 1 # and add a hit so we can divide by the correct amount to find the avg

        if hits == 0:
            avgs.append(None)
        else:
            avgs.append(total / hits)
    return avgs

# init function for the animation
def init():
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
    lp_N_time_counter.set_data(x, y)
    lp_SE_time_counter.set_data(x, y)
    lp_SW_time_counter.set_data(x, y)
    return list_plots

if __name__ == '__main__':

    this_date = input("\nWhich date? ")

    print("Make sure all of the *'s are the same number")

    TimeTable = Time_Table(this_date)
    ZeroHour = datetime.combine(Date_P2D(this_date), (time(second=0)))
    LastHour = datetime.combine(Date_P2D(this_date), (time(hour=23, minute=59)))

    NW_dets, NE_dets, SW_dets, SE_dets = Split2Regions()
    N_dets = NW_dets + NE_dets

    print("\nGrabbing L0L1 data...")
    L0L1_dict = L0L1(this_date)
    print("\nFinding rates of change...")
    rate_warns = FindRates(L0L1_dict)
    print("\nExtracting data...")
    detectors_placements, detectors_rates = ExtractL0rates(L0L1_dict, TimeTable)
    print()
    print("\nGrabbing NLDN data...")
    NLDN_dict, PC_Times, Peak_Currents = NLDN(this_date)
    print("\nExtracting data...")
    NLDNonTASD = ExtractNLDN(NLDN_dict, TimeTable)

    print("\nFinding N rate cutoffs")
    N = RateCutoff(L0L1_dict, N_dets, TimeTable)
    print("Finding SW rate cutoffs")
    SW = RateCutoff(L0L1_dict, SW_dets, TimeTable)
    print("Finding SE rate cutoffs")
    SE = RateCutoff(L0L1_dict, SE_dets, TimeTable)

    xLabels_NLDN, xLabels_OneD  = [], []
    for i in range(8):
        xLabels_NLDN.append(ZeroHour + i * THREE_HOURS)
    for i in range(4):
        xLabels_OneD.append(ZeroHour + i * SIX_HOURS)

    min_max_flag = False
    min_rate = 1000000
    max_rate = -1000000

    for rate in N:
        if rate is not None:
            min_max_flag = True
            if rate < min_rate:
                min_rate = rate
            if rate > max_rate:
                max_rate = rate
    for rate in SW:
        if rate is not None:
            min_max_flag = True
            if rate < min_rate:
                min_rate = rate
            if rate > max_rate:
                max_rate = rate
    for rate in SE:
        if rate is not None:
            min_max_flag = True
            if rate < min_rate:
                min_rate = rate
            if rate > max_rate:
                max_rate = rate

    if not min_max_flag:
        min_rate = 0
        max_rate = 0
    min_rate += -.5
    max_rate += .5

    # all this stuff below here is plot creation stuff
    # a bunch of it consists of tiny tweaks to make the plots look better and more readable
    # most all of it is pretty self explanitory
    fig = plt.figure(constrained_layout=False)
    fig.suptitle(this_date, fontsize=10)

    cmap = mpl.colors.ListedColormap(CMAP_COLORS)
    norm = mpl.colors.BoundaryNorm(CMAP_BOUNDS, cmap.N)

    gs_left = fig.add_gridspec(5, 3, left=0.08, right=0.48, top=.92, bottom=.08, wspace=0, hspace=0.5)
    gs_right = fig.add_gridspec(2, 4, left=0.53, right=0.98, wspace=0.6, hspace=0.3)

    plt.rc('xtick', labelsize = 6)
    plt.rc('ytick', labelsize = 6)

    TASDax = fig.add_subplot(gs_left[:3, :3])
    TASDax.set_xlim(-20, 20)
    TASDax.set_ylim(-23, 18)
    sp_sensors = TASDax.scatter(tasdx, tasdy, c='yellow', s=7, marker='.')
    sp_sensor_readings = TASDax.scatter([], [], c=[], s=7, cmap=cmap, norm=norm, marker='s', vmin = -5, vmax = 5)
    sp_lightning_readings = TASDax.scatter([], [], c='black', s=10, marker='+')
    plt.colorbar(sp_sensor_readings, cmap=cmap, norm=norm)

    NLDNax = fig.add_subplot(gs_left[3:, :3])
    NLDNax.grid(True)
    NLDNax.set_xlim(ZeroHour, LastHour)
    NLDNax.set_ylim(-250, 250)
    NLDNax.set_xticks(xLabels_NLDN)
    NLDNax.set_xlabel("Time")
    NLDNax.set_ylabel("Peak Current")
    NLDNax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    sp_lightning_level = NLDNax.scatter(PC_Times, Peak_Currents, c='black', s=7, marker='+')
    lp_NLDN_time_counter, = NLDNax.plot([], [], lw=1, c='blue')

    Nax = fig.add_subplot(gs_right[0, 1:3])
    Nax.set_title("N")
    Nax.set_xlim(ZeroHour, LastHour)
    Nax.set_ylim(min_rate, max_rate)
    Nax.set_xticks(xLabels_OneD)
    Nax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    #Nax.plot(TimeTable, N, lw=1, c='green')
    Nax.scatter(TimeTable, N, s=1, c='green')
    lp_N_time_counter, = Nax.plot([], [], lw=1, c='blue')

    SEax = fig.add_subplot(gs_right[1, 2:])
    SEax.set_title("SE")
    SEax.set_xlim(ZeroHour, LastHour)
    SEax.set_ylim(min_rate, max_rate)
    SEax.set_xticks(xLabels_OneD)
    SEax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    #SEax.plot(TimeTable, SE, lw=1, c='green')
    SEax.scatter(TimeTable, SE, s=1, c='green')
    lp_SE_time_counter, = SEax.plot([], [], lw=1, c='blue')

    SWax = fig.add_subplot(gs_right[1, :2])
    SWax.set_title("SW")
    SWax.set_xlim(ZeroHour, LastHour)
    SWax.set_ylim(min_rate, max_rate)
    SWax.set_xticks(xLabels_OneD)
    SWax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    #SWax.plot(TimeTable, SW, lw=1, c='green')
    SWax.scatter(TimeTable, SW, s=1, c='green')
    lp_SW_time_counter, = SWax.plot([], [], lw=1, c='blue')

    list_plots = [sp_sensor_readings, sp_lightning_readings, lp_NLDN_time_counter, lp_N_time_counter, lp_SE_time_counter, lp_SW_time_counter]

    anim = animation.FuncAnimation(fig, update, init_func=init, interval=ANI_SPEED, blit=True, repeat=True, frames=144)

    print()
    for warning in rate_warns:
        print("Warning: " + warning[0] + " at " + warning[1].strftime("%H:%M:%S") + " is above " + str(RATE_WARNING) + "%")

    save = str(input("\nSave? [y/n] "))
    while (save != "y" and save != "n"):
        save = str(input("Invalid response. Save? [y/n] "))

    if (save == "y"):
        print("Saving...")
        HTML(anim.to_html5_video())
        place = "Movies/" + str(this_date)
        anim.save(place + "/RateRVcutoff.mp4", fps=1, writer="ffmpeg", dpi=1000, bitrate=5000)

    plt.show()
