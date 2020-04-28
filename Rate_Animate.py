import geopy as gp
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from taTools import *

# TODO:
#   -put colorbar in correct area                               DONE
#   -fix colorbar color, vmin, and vmax                         DONE
#   -make and animate a lineplot on ax3                         DONE
#   -how does gridspec work? (lines defining ax1, ax2, and ax3) DONE
#   -save animation
#   -legend for time?
#   -define everything as a proper function
#   -better size for histos                                     DONE
#   -check times (weird differences that have 141 times vs 144)

#------------------------------------------|Config|------------------------------------------#

date = "140927"
dector_filename = "DataDates/" + date + "/L0L1.txt"  #file names
lightning_filename = "DataDates/" + date + "/NLDN.txt"
early_time = 000000 #times you want to look between
late_time  = 240000
#int_det = 1620
#int_det = int(input("What detector would you like to view? "))

wspace = 1 #space between the subplots horizontally
hspace = .5 #space between the subplots vertically

take_out_dontuse = True
take_out_warn = False

anispeed = 750 #animation speed - lower is faster
lower_percent = -1 #lower percent of color grad
higher_percent = -1 * lower_percent #higher percent of color grad

size_of_lightning = 13 #size of the squares and crosses
size_of_sensors = 10
size_of_sensor_data = 16

#------------------------------------------|Initalization|------------------------------------------#
tasdnum,tasdx,tasdy,tasdz =[],[],[],[]
tasdxyz(tasdnum,tasdx,tasdy,tasdz)

tasdlat,tasdlon,tasdalt = [],[],[]
tasdgps(tasdlat,tasdlon,tasdalt)

#for sensors
s_yymmdd = []
s_hhmmss = []
s_hitdetnum = []
s_lv0rate = []
s_lv1rate = []
s_warn = []
s_dontuse = []
s_quality = []

#for lighting
l_date = []
l_time = []
l_lat = []
l_long = []
l_peakcurrent = []
l_type = []

#for TGF
TGF_date = []
TGF_time = []
TGF_center_sensor = []

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+  Import Data  +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
file = open(dector_filename,'r')

debug_count = 0

for line in file:
    columns = line.split()

    if (int(columns[1]) > early_time and int(columns[1]) < late_time):
        if (not take_out_dontuse or int(columns[5]) == 0):
            if(not take_out_warn or int(columns[6]) == 0):
                debug_count += 1
                s_yymmdd.append(int(columns[0]))
                s_hhmmss.append(int(columns[1]))
                s_hitdetnum.append(int(columns[2]))
                s_lv0rate.append(float(columns[3]))
                s_lv1rate.append(float(columns[4]))
                s_dontuse.append(int(columns[5]))
                s_warn.append(int(columns[6]))
                s_quality.append(int(columns[7]))

print("Found " + str(debug_count) + " data points for sensors")

file.close()

#open and parse lighting file
file = open(lightning_filename,'r')

debug_count = 0

for line in file:
    columns = line.split()

    debug_count += 1
    l_date.append(columns[0])
    l_time.append(columns[1])
    l_lat.append(columns[2])
    l_long.append(columns[3])
    l_peakcurrent.append(float(columns[4]))
    l_type.append(columns[5])

print("Found " + str(debug_count) + " data points for lightning")

file.close()

#open and parse TGR events
file = open("TGF.txt",'r')

debug_count = 0

for line in file:
    columns = line.split()

    if (date == columns[0]):
        TGF_date.append(columns[0])
        TGF_time.append(columns[1])
        TGF_center_sensor.append(columns[2])
        debug_count += 1


print("Found " + str(debug_count) + " TGF events")

file.close()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-==-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+  Set Data as Readable  +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-==-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

#-----------------------------------------------------Setting-the-det-num--------------------------------------------------------
if (len(TGF_center_sensor) > 0):
    int_det = int(TGF_center_sensor[0])
else:
    int_det = None

#-----------------------------------------------------Easy-use-for-time--------------------------------------------------------
#will create a list called "times" that holds a unique values for each time
times = [s_hhmmss[0]]

for i in range(len(s_hhmmss) - 1):
    if (s_hhmmss[i] != s_hhmmss[i + 1]):
        times.append(s_hhmmss[i + 1])

print("Done " + str(len(times)) + " times")

#-----------------------------------------------Finding-the-x,y-for-each-sensor--------------------------------------------------
s_datax = []
s_datay = []
debug_count = 0
debug_count_2 = 0
flag = 0

for i in range(len(s_hitdetnum)):
    for j in range(len(tasdnum[0])):
        if (s_hitdetnum[i] == tasdnum[0][j]):
            s_datax.append(tasdx[j])
            s_datay.append(tasdy[j])
            flag = 1
            debug_count += 1
    if (flag == 0):
        s_datax.append(None)
        s_datay.append(None)
        debug_count_2 =+ 1
    flag = 0

print("Made " + str(debug_count) + " hitdetnums into x,y with " + str(debug_count_2) + " null points")

#------------------------------------------------Changing-lighting-time-data-------------------------------------------------------
l_time_per_hour = []
debug_count = 0

for i in range(len(l_peakcurrent)):
    temp = l_time[i].split(":")
    hours = int(temp[0])
    minutes = int(temp[1])
    seconds = float(temp[2])
    l_time_per_hour.append(hours + minutes / 60 + seconds / 360)
    debug_count += 1

print("Fixed " + str(debug_count) + " lighting time data points")

#---------------------------------------------Changing-lighting-placement-data-----------------------------------------------------
l_data_xy = [[None, None]]
lighting_data_place = []
debug_count = 0

for i in range(len(times)):
    for j in range(len(l_time_per_hour)):
        if (l_time_per_hour[j] <= float(times[i]/10000)):
            l_gps = gp.point.Point(l_lat[j], l_long[j], 0)
            lx,ly,lz = gps2cart(l_gps)
            l_data_xy.append([lx, ly])
    lighting_data_place.append(l_data_xy)
    l_data_xy = [[None, None]]
    flag = 0
    debug_count += 1

print("Made " + str(debug_count) + " lighting placement frames")

#------------------------------------------Finding-all-the-rates-of-change-for-color-----------------------------------------------
sensor_data_level_holder = []
debug_count = 0

for i in range(len(s_hitdetnum)):
    for j in range(i + 1, len(s_hitdetnum)):
        if (s_hitdetnum[i] == s_hitdetnum[j]):
            sensor_data_level_holder.append((s_lv0rate[j] - s_lv0rate[i]) * 100 / s_lv0rate[i])
            debug_count += 1
            break

extra_null_points = 1000

for i in range(extra_null_points): #dirty way to fix this array for not having enough points at the end of the cycle
    sensor_data_level_holder.append(0) #(for rate of change, take this one and next one, but at end of line there is no next one)

print("Made " + str(debug_count) + " + " + str(extra_null_points) + " sensor data points into rates")

#-------------------------------------------------Finding-dectors-for-histo---------------------------------------------------
print("Finding sensors for histo...")

#detector numbers for 3x3
TL = int_det - 99
TM = int_det + 1
TR = int_det + 101
ML = int_det - 100
MR = int_det + 100
BL = int_det - 101
BM = int_det - 1
BR = int_det + 99

#detector numbers for 5x5
#added later, appends to lists 10-25
ULL = int_det - 198
UL = int_det - 98
UM = int_det + 2
UR = int_det + 102
URR = int_det + 202
TLL = int_det - 199
TRR = int_det + 201
MLL = int_det - 200
MRR = int_det + 200
BLL = int_det - 201
BRR = int_det + 199
LLL = int_det - 202
LL = int_det - 102
LM = int_det - 2
LR = int_det + 98
LRR = int_det + 198

#-------------------------------------------------Finding-data-for-histo----------------------------------------------------
print("Finding data for histo...")

dlv0rate1 = []
dtime1 = []

dlv0rate2 = []
dtime2 = []

dlv0rate3 = []
dtime3 = []

dlv0rate4 = []
dtime4 = []

dlv0rate5 = []
dtime5 = []

dlv0rate6 = []
dtime6 = []

dlv0rate7 = []
dtime7 = []

dlv0rate8 = []
dtime8 = []

dlv0rate9 = []
dtime9 = []

dlv0rate10 = []
dtime10 = []

dlv0rate11 = []
dtime11 = []

dlv0rate12 = []
dtime12 = []

dlv0rate13 = []
dtime13 = []

dlv0rate14 = []
dtime14 = []

dlv0rate15 = []
dtime15 = []

dlv0rate16 = []
dtime16 = []

dlv0rate17 = []
dtime17 = []

dlv0rate18 = []
dtime18 = []

dlv0rate19 = []
dtime19 = []

dlv0rate20 = []
dtime20 = []

dlv0rate21 = []
dtime21 = []

dlv0rate22 = []
dtime22 = []

dlv0rate23 = []
dtime23 = []

dlv0rate24 = []
dtime24 = []

dlv0rate25 = []
dtime25 = []

for i in range(len(s_hitdetnum)):

    if TL == s_hitdetnum[i]:
        dlv0rate1.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime1.append(hours + minutes / 60 + seconds / 360)

    if TM == s_hitdetnum[i]:
        dlv0rate2.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime2.append(hours + minutes / 60 + seconds / 360)

    if TR == s_hitdetnum[i]:
        dlv0rate3.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime3.append(hours + minutes / 60 + seconds / 360)

    if ML == s_hitdetnum[i]:
        dlv0rate4.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime4.append(hours + minutes / 60 + seconds / 360)

    if int_det == s_hitdetnum[i]:
        dlv0rate5.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime5.append(hours + minutes / 60 + seconds / 360)

    if MR == s_hitdetnum[i]:
        dlv0rate6.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime6.append(hours + minutes / 60 + seconds / 360)

    if BL == s_hitdetnum[i]:
        dlv0rate7.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime7.append(hours + minutes / 60 + seconds / 360)

    if BM == s_hitdetnum[i]:
        dlv0rate8.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime8.append(hours + minutes / 60 + seconds / 360)

    if BR == s_hitdetnum[i]:
        dlv0rate9.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime9.append(hours + minutes / 60 + seconds / 360)

    if ULL == s_hitdetnum[i]:
        dlv0rate10.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime10.append(hours + minutes / 60 + seconds / 360)

    if UL == s_hitdetnum[i]:
        dlv0rate11.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime11.append(hours + minutes / 60 + seconds / 360)

    if UM == s_hitdetnum[i]:
        dlv0rate12.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime12.append(hours + minutes / 60 + seconds / 360)

    if UR == s_hitdetnum[i]:
        dlv0rate13.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime13.append(hours + minutes / 60 + seconds / 360)

    if URR == s_hitdetnum[i]:
        dlv0rate14.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime14.append(hours + minutes / 60 + seconds / 360)

    if TLL == s_hitdetnum[i]:
        dlv0rate15.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime15.append(hours + minutes / 60 + seconds / 360)

    if TRR == s_hitdetnum[i]:
        dlv0rate16.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime16.append(hours + minutes / 60 + seconds / 360)

    if MLL == s_hitdetnum[i]:
        dlv0rate17.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime17.append(hours + minutes / 60 + seconds / 360)

    if MRR == s_hitdetnum[i]:
        dlv0rate18.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime18.append(hours + minutes / 60 + seconds / 360)

    if BLL == s_hitdetnum[i]:
        dlv0rate19.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime19.append(hours + minutes / 60 + seconds / 360)

    if BRR == s_hitdetnum[i]:
        dlv0rate20.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime20.append(hours + minutes / 60 + seconds / 360)

    if LLL == s_hitdetnum[i]:
        dlv0rate21.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime21.append(hours + minutes / 60 + seconds / 360)

    if LL == s_hitdetnum[i]:
        dlv0rate22.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime22.append(hours + minutes / 60 + seconds / 360)

    if LM == s_hitdetnum[i]:
        dlv0rate23.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime23.append(hours + minutes / 60 + seconds / 360)

    if LR == s_hitdetnum[i]:
        dlv0rate24.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime24.append(hours + minutes / 60 + seconds / 360)

    if LRR == s_hitdetnum[i]:
        dlv0rate25.append(s_lv0rate[i])
        hours = int(s_hhmmss[i] / 10000)
        minutes = int(s_hhmmss[i] / 100) - (hours * 100)
        seconds = s_hhmmss[i] - (hours * 10000) - (minutes * 100)
        dtime25.append(hours + minutes / 60 + seconds / 360)

#-------------------------------------------------------Fixing-TGF-times--------------------------------------------------------
TGF_fixed_time = []

for time in TGF_time:
    temp = time.split(":")
    hours = int(temp[0])
    minutes = int(temp[1])
    seconds = float(temp[2])
    TGF_fixed_time.append(hours + minutes / 60 + seconds / 360)

TGF_fixed_time.append(None)
TGF_fixed_time.append(None)
#--------------------------------------------Putting-times-in-easy-to-read-matrices--------------------------------------------
sensor_data_place = []
sensor_data_level = []
hit_x_y = []
hit_c = []

print("Making data readable...")

for i in range(len(times)):
    for j in range(len(s_hhmmss)):
        if (int(s_hhmmss[j]) == int(times[i])):
            hit_x_y.append([s_datax[j], s_datay[j]])
            hit_c.append(sensor_data_level_holder[j])

    sensor_data_place.append(hit_x_y)
    sensor_data_level.append(hit_c)
    hit_x_y = []
    hit_c = []

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+  Animation  +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

print("Building...")

def init():
    lp_time_counter.set_data([], [])
    lp_time_counter1.set_data([], [])
    lp_time_counter2.set_data([], [])
    lp_time_counter3.set_data([], [])
    lp_time_counter4.set_data([], [])
    lp_time_counter5.set_data([], [])
    lp_time_counter6.set_data([], [])
    lp_time_counter7.set_data([], [])
    lp_time_counter8.set_data([], [])
    lp_time_counter9.set_data([], [])
    lp_time_counter10.set_data([], [])
    lp_time_counter11.set_data([], [])
    lp_time_counter12.set_data([], [])
    lp_time_counter13.set_data([], [])
    lp_time_counter14.set_data([], [])
    lp_time_counter15.set_data([], [])
    lp_time_counter16.set_data([], [])
    lp_time_counter17.set_data([], [])
    lp_time_counter18.set_data([], [])
    lp_time_counter19.set_data([], [])
    lp_time_counter20.set_data([], [])
    lp_time_counter21.set_data([], [])
    lp_time_counter22.set_data([], [])
    lp_time_counter23.set_data([], [])
    lp_time_counter24.set_data([], [])
    lp_time_counter25.set_data([], [])
    sp_sensor_readings.set_offsets([[], []])
    sp_lightning_readings.set_offsets([[], []])
    return listplots

def update(frame):

    x = frame * 1/6 + int(early_time/10000) + (int(early_time/100) % 100) * 1/60 + (int(early_time % 10000) * 1/360)
    y = np.linspace(-250, 1000, 250) #time counter function

    lp_time_counter.set_data(x, y)

    lp_time_counter1.set_data(x, y)
    lp_time_counter2.set_data(x, y)
    lp_time_counter3.set_data(x, y)
    lp_time_counter4.set_data(x, y)
    lp_time_counter5.set_data(x, y)
    lp_time_counter6.set_data(x, y)
    lp_time_counter7.set_data(x, y)
    lp_time_counter8.set_data(x, y)
    lp_time_counter9.set_data(x, y)
    lp_time_counter10.set_data(x, y)
    lp_time_counter11.set_data(x, y)
    lp_time_counter12.set_data(x, y)
    lp_time_counter13.set_data(x, y)
    lp_time_counter14.set_data(x, y)
    lp_time_counter15.set_data(x, y)
    lp_time_counter16.set_data(x, y)
    lp_time_counter17.set_data(x, y)
    lp_time_counter18.set_data(x, y)
    lp_time_counter19.set_data(x, y)
    lp_time_counter20.set_data(x, y)
    lp_time_counter21.set_data(x, y)
    lp_time_counter22.set_data(x, y)
    lp_time_counter23.set_data(x, y)
    lp_time_counter24.set_data(x, y)
    lp_time_counter25.set_data(x, y)

    sp_sensor_readings.set_offsets(sensor_data_place[frame])
    sp_lightning_readings.set_offsets(lighting_data_place[frame])

    sp_sensor_readings.set_array(np.asarray(sensor_data_level[frame]))

    return listplots

print(" Figure") #debug
fig = plt.figure(constrained_layout=False)

#set the title
title = "On " + str(date) + " at "
for i in range(len(TGF_time)):
    temp = TGF_time[i].split(".")
    title = title + str(temp[0]) + " | " + str(TGF_center_sensor[i]) + ", "
title = title.rstrip()
title = title.rstrip(",")
fig.suptitle(title, fontsize=20)

gs1 = fig.add_gridspec(5, 3, left=0.08, right=0.48, top=.92, bottom=.08, wspace=1, hspace=0.5)

print(" Sensors") #debug
j_ax1 = fig.add_subplot(gs1[:3, :3]) #setting subplot location
j_ax1.set_xlim(-20, 20) #limits
j_ax1.set_ylim(-23, 18)
sp_sensors = j_ax1.scatter(tasdx, tasdy, c='r', s=size_of_sensors, marker='s') #this is for placing the general sensors (the red squares)
sp_lightning_readings = j_ax1.scatter([], [], c='r', s=size_of_lightning, marker='x') #this is for showing the nldn readings (the red x's)
sp_sensor_readings = j_ax1.scatter([], [], c=[], s=size_of_sensor_data, cmap="jet", marker='s', vmin = -1, vmax = 1) #this is for showing the sensor readings
plt.colorbar(sp_sensor_readings, cmap='jet')

print(" NLDN") #debug
j_ax2 = fig.add_subplot(gs1[3:, :3])
j_ax2.grid(True)
j_ax2.set_xlim(0,24)
j_ax2.set_ylim(-250,250)
j_ax2.set_xticks((0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24))
j_ax2.set_yticks((-250, -200, -150, -100, -50, 0, 50, 100, 150, 200, 250))
sp_lightning_level = j_ax2.scatter(l_time_per_hour, l_peakcurrent, c='r', s=size_of_lightning/2, marker='x')   #input np.arrays of lighting data
lp_time_counter, = j_ax2.plot([], [], lw=1) #this is for iteratoring along the time on the bottom graph
lp_TGF_NLDN_0 = j_ax2.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[-250,250],lw=1, c='g')
lp_TGF_NLDN_1 = j_ax2.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[-250,250],lw=1, c='g')
lp_TGF_NLDN_2 = j_ax2.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[-250,250],lw=1, c='g')

print(" Histos") #debug
gs2 = fig.add_gridspec(5, 5, left=0.53, right=0.98, wspace=0.3, hspace=0.3)

ax1 = fig.add_subplot(gs2[1,1])
ax1.set_xlim(0,24)
ax1.set_ylim(700,760)
ax1.set_xticks([])
ax1.set_yticks([])
ax1.plot(dtime1, dlv0rate1, lw=1)
ax1.set_title(TL, fontsize=6)
lp_time_counter1, = ax1.plot([], [], lw=1)
lp_TGF_0_1 = ax1.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_1 = ax1.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_1 = ax1.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax2 = fig.add_subplot(gs2[1,2])
ax2.set_xlim(0,24)
ax2.set_ylim(700,760)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.plot(dtime2, dlv0rate2, lw=1)
ax2.set_title(TM, fontsize=6)
lp_time_counter2, = ax2.plot([], [], lw=1)
lp_TGF_0_2 = ax2.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_2 = ax2.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_2 = ax2.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax3 = fig.add_subplot(gs2[1,3])
ax3.set_xlim(0,24)
ax3.set_ylim(700,760)
ax3.set_xticks([])
ax3.set_yticks([])
ax3.plot(dtime3, dlv0rate3, lw=1)
ax3.set_title(TR, fontsize=6)
lp_time_counter3, = ax3.plot([], [], lw=1)
lp_TGF_0_3 = ax3.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_3 = ax3.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_3 = ax3.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax4 = fig.add_subplot(gs2[2,1])
ax4.set_xlim(0,24)
ax4.set_ylim(700,760)
ax4.set_xticks([])
ax4.set_yticks([])
ax4.plot(dtime4, dlv0rate4, lw=1)
ax4.set_title(ML, fontsize=6)
lp_time_counter4, = ax4.plot([], [], lw=1)
lp_TGF_0_4 = ax4.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_4 = ax4.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_4 = ax4.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax5 = fig.add_subplot(gs2[2,2])
ax5.set_xlim(0,24)
ax5.set_ylim(700,760)
ax5.set_xticks([])
ax5.set_yticks([])
ax5.plot(dtime5, dlv0rate5, lw=1)
ax5.set_title(int_det, fontsize=6)
lp_time_counter5, = ax5.plot([], [], lw=1)
lp_TGF_0_5 = ax5.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_5 = ax5.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_5 = ax5.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax6 = fig.add_subplot(gs2[2,3])
ax6.set_xlim(0,24)
ax6.set_ylim(700,760)
ax6.set_xticks([])
ax6.set_yticks([])
ax6.plot(dtime6, dlv0rate6, lw=1)
ax6.set_title(MR, fontsize=6)
lp_time_counter6, = ax6.plot([], [], lw=1)
lp_TGF_0_6 = ax6.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_6 = ax6.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_6 = ax6.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax7 = fig.add_subplot(gs2[3,1])
ax7.set_xlim(0,24)
ax7.set_ylim(700,760)
ax7.set_xticks([])
ax7.set_yticks([])
ax7.plot(dtime7, dlv0rate7, lw=1)
ax7.set_title(BL, fontsize=6)
lp_time_counter7, = ax7.plot([], [], lw=1)
lp_TGF_0_7 = ax7.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_7 = ax7.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_7 = ax7.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax8 = fig.add_subplot(gs2[3,2])
ax8.set_xlim(0,24)
ax8.set_ylim(700,760)
ax8.set_xticks([])
ax8.set_yticks([])
ax8.plot(dtime8, dlv0rate8, lw=1)
ax8.set_title(BM, fontsize=6)
lp_time_counter8, = ax8.plot([], [], lw=1)
lp_TGF_0_8 = ax8.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_8 = ax8.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_8 = ax8.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax9 = fig.add_subplot(gs2[3,3])
ax9.set_xlim(0,24)
ax9.set_ylim(700,760)
ax9.set_xticks([])
ax9.set_yticks([])
ax9.plot(dtime9, dlv0rate9, lw=1)
ax9.set_title(BR, fontsize=6)
lp_time_counter9, = ax9.plot([], [], lw=1)
lp_TGF_0_9 = ax9.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_9 = ax9.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_9 = ax9.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax10 = fig.add_subplot(gs2[0,0])
ax10.set_xlim(0,24)
ax10.set_ylim(700,760)
ax10.set_xticks([])
ax10.plot(dtime10, dlv0rate10, lw=1)
ax10.set_title(ULL, fontsize=6)
lp_time_counter10, = ax10.plot([], [], lw=1)
lp_TGF_0_10 = ax10.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_10 = ax10.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_10 = ax10.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax11 = fig.add_subplot(gs2[0,1])
ax11.set_xlim(0,24)
ax11.set_ylim(700,760)
ax11.set_xticks([])
ax11.set_yticks([])
ax11.plot(dtime11, dlv0rate11, lw=1)
ax11.set_title(UL, fontsize=6)
lp_time_counter11, = ax11.plot([], [], lw=1)
lp_TGF_0_11 = ax11.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_11 = ax11.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_11 = ax11.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax12 = fig.add_subplot(gs2[0,2])
ax12.set_xlim(0,24)
ax12.set_ylim(700,760)
ax12.set_xticks([])
ax12.set_yticks([])
ax12.plot(dtime12, dlv0rate12, lw=1)
ax12.set_title(UM, fontsize=6)
lp_time_counter12, = ax12.plot([], [], lw=1)
lp_TGF_0_12 = ax12.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_12 = ax12.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_12 = ax12.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax13 = fig.add_subplot(gs2[0,3])
ax13.set_xlim(0,24)
ax13.set_ylim(700,760)
ax13.set_xticks([])
ax13.set_yticks([])
ax13.plot(dtime13, dlv0rate13, lw=1)
ax13.set_title(UR, fontsize=6)
lp_time_counter13, = ax13.plot([], [], lw=1)
lp_TGF_0_13 = ax13.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_13 = ax13.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_13 = ax13.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax14 = fig.add_subplot(gs2[0,4])
ax14.set_xlim(0,24)
ax14.set_ylim(700,760)
ax14.set_xticks([])
ax14.set_yticks([])
ax14.plot(dtime14, dlv0rate14, lw=1)
ax14.set_title(URR, fontsize=6)
lp_time_counter14, = ax14.plot([], [], lw=1)
lp_TGF_0_14 = ax14.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_14 = ax14.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_14 = ax14.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax15 = fig.add_subplot(gs2[1,0])
ax15.set_xlim(0,24)
ax15.set_ylim(700,760)
ax15.set_xticks([])
ax15.plot(dtime15, dlv0rate15, lw=1)
ax15.set_title(TLL, fontsize=6)
lp_time_counter15, = ax15.plot([], [], lw=1)
lp_TGF_0_15 = ax15.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_15 = ax15.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_15 = ax15.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax16 = fig.add_subplot(gs2[1,4])
ax16.set_xlim(0,24)
ax16.set_ylim(700,760)
ax16.set_xticks([])
ax16.set_yticks([])
ax16.plot(dtime16, dlv0rate16, lw=1)
ax16.set_title(TRR, fontsize=6)
lp_time_counter16, = ax16.plot([], [], lw=1)
lp_TGF_0_16 = ax16.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_16 = ax16.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_16 = ax16.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax17 = fig.add_subplot(gs2[2,0])
ax17.set_xlim(0,24)
ax17.set_ylim(700,760)
ax17.set_xticks([])
ax17.plot(dtime17, dlv0rate17, lw=1)
ax17.set_title(MLL, fontsize=6)
lp_time_counter17, = ax17.plot([], [], lw=1)
lp_TGF_0_17 = ax17.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_17 = ax17.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_17 = ax17.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax18 = fig.add_subplot(gs2[2,4])
ax18.set_xlim(0,24)
ax18.set_ylim(700,760)
ax18.set_xticks([])
ax18.set_yticks([])
ax18.plot(dtime18, dlv0rate18, lw=1)
ax18.set_title(MRR, fontsize=6)
lp_time_counter18, = ax18.plot([], [], lw=1)
lp_TGF_0_18 = ax18.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_18 = ax18.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_18 = ax18.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax19 = fig.add_subplot(gs2[3,0])
ax19.set_xlim(0,24)
ax19.set_ylim(700,760)
ax19.set_xticks([])
ax19.plot(dtime19, dlv0rate19, lw=1)
ax19.set_title(BLL, fontsize=6)
lp_time_counter19, = ax19.plot([], [], lw=1)
lp_TGF_0_19 = ax19.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_19 = ax19.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_19 = ax19.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax20 = fig.add_subplot(gs2[3,4])
ax20.set_xlim(0,24)
ax20.set_ylim(700,760)
ax20.set_xticks([])
ax20.set_yticks([])
ax20.plot(dtime20, dlv0rate20, lw=1)
ax20.set_title(BRR, fontsize=6)
lp_time_counter20, = ax20.plot([], [], lw=1)
lp_TGF_0_20 = ax20.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_20 = ax20.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_20 = ax20.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax21 = fig.add_subplot(gs2[4,0])
ax21.set_xlim(0,24)
ax21.set_ylim(700,760)
ax21.set_xticks([0, 6, 12, 18, 24])
ax21.plot(dtime21, dlv0rate21, lw=1)
ax21.set_title(LLL, fontsize=6)
lp_time_counter21, = ax21.plot([], [], lw=1)
lp_TGF_0_21 = ax21.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_21 = ax21.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_21 = ax21.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax22 = fig.add_subplot(gs2[4,1])
ax22.set_xlim(0,24)
ax22.set_ylim(700,760)
ax22.set_xticks([0, 6, 12, 18, 24])
ax22.set_yticks([])
ax22.plot(dtime22, dlv0rate22, lw=1)
ax22.set_title(LL, fontsize=6)
lp_time_counter22, = ax22.plot([], [], lw=1)
lp_TGF_0_22 = ax22.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_22 = ax22.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_22 = ax22.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax23 = fig.add_subplot(gs2[4,2])
ax23.set_xlim(0,24)
ax23.set_ylim(700,760)
ax23.set_xticks([0, 6, 12, 18, 24])
ax23.set_yticks([])
ax23.plot(dtime23, dlv0rate23, lw=1)
ax23.set_title(LM, fontsize=6)
lp_time_counter23, = ax23.plot([], [], lw=1)
lp_TGF_0_23 = ax23.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_23 = ax23.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_23 = ax23.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax24 = fig.add_subplot(gs2[4,3])
ax24.set_xlim(0,24)
ax24.set_ylim(700,760)
ax24.set_xticks([0, 6, 12, 18, 24])
ax24.set_yticks([])
ax24.plot(dtime24, dlv0rate24, lw=1)
ax24.set_title(LR, fontsize=6)
lp_time_counter24, = ax24.plot([], [], lw=1)
lp_TGF_0_24 = ax24.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_24 = ax24.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_24 = ax24.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

ax25 = fig.add_subplot(gs2[4,4])
ax25.set_xlim(0,24)
ax25.set_ylim(700,760)
ax25.set_xticks([0, 6, 12, 18, 24])
ax25.set_yticks([])
ax25.plot(dtime25, dlv0rate25, lw=1)
ax25.set_title(LRR, fontsize=6)
lp_time_counter25, = ax25.plot([], [], lw=1)
lp_TGF_0_25 = ax25.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_1_25 = ax25.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[700,760],lw=1, c='y', alpha=.5)
lp_TGF_2_25 = ax25.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[700,760],lw=1, c='y', alpha=.5)

listplots = [sp_sensor_readings, sp_lightning_readings, lp_time_counter, lp_time_counter1, lp_time_counter2, lp_time_counter3, lp_time_counter4, lp_time_counter5, lp_time_counter6, lp_time_counter7, lp_time_counter8, lp_time_counter9, lp_time_counter10, lp_time_counter11, lp_time_counter12, lp_time_counter13, lp_time_counter14, lp_time_counter15, lp_time_counter16, lp_time_counter17, lp_time_counter18, lp_time_counter19, lp_time_counter20, lp_time_counter21, lp_time_counter22, lp_time_counter23, lp_time_counter24, lp_time_counter25]

print(" Animation")
anim = animation.FuncAnimation(fig, update, init_func=init, interval=anispeed, blit=True, repeat=True, frames=len(sensor_data_place))

print("Done")
plt.show()
