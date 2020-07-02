#Code written by Crush302

import geopy as gp
import numpy as np

import matplotlib.colors as mcolors #check if i need this
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from taTools import *

from IPython.display import HTML
animation.rcParams["animation.writer"] = "ffmpeg"

#NLDN inbetween the ten mins

# TODO:
#   -put colorbar in correct area                               DONE
#   -fix colorbar color, vmin, and vmax                         DONE
#   -make and animate a lineplot on ax3                         DONE
#   -how does gridspec work? (lines defining ax1, ax2, and ax3) DONE
#   -save animation                                             DONE
#   -legend for time?                                           N/A
#   -define everything as a proper function
#   -better size for histos                                     DONE
#   -check times (weird differences that have 141 times vs 144)
#   -are the percent changes correct?
#   -take out TGF stuff

#------------------------------------------|Config|------------------------------------------#

date = str(input("What date? "))
dector_filename = "DataDates/" + date + "/L0L1.txt"  #file names
lightning_filename = "DataDates/" + date + "/NLDN.txt"
default_sensor = 1620
#early_time = 100000 #times you want to look between
#late_time  = 240000

bounds = [-3, -1, -.5, .5, 1, 3] #Set the bounds for the color map

wspace = 1 #space between the subplots horizontally
hspace = .5 #space between the subplots vertically

take_out_dontuse = True
take_out_warn = False

anispeed = 1000 #animation speed - lower is faster
lower_percent = -1 #lower percent of color grad
higher_percent = -1 * lower_percent #higher percent of color grad

size_of_lightning = 7 #size of the squares and crosses
size_of_sensors = 7
size_of_sensor_data = 7

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
lv0rate_time_sensitive = []
hitdetnum_time_sensitive = []
hhmmss_time_sensitive = []

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

print()
print("Getting Data...")
'''
#open and parse TGF events
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

TGF_number = int(input("Which TGF event do you want to look at, or all day? [0 for all day, 1 for first, etc] "))

if (TGF_number == 0):
    all_day = True
else:
    all_day = False
    TGF_number -= 1

if all_day:
    early_time = 000000
    late_time = 240000
else:
    temp = TGF_time[TGF_number].split(":")
    hours = int(temp[0])
    minutes = int(temp[1])
    seconds = float(temp[2])

    early_time = (hours - 2) * 10000 + (int((minutes)/10) * 10) * 100
    late_time = (hours + 1) * 10000 + (int(minutes/10) * 10) * 100

diff = 0
if (early_time < 0):
    diff = -early_time
    early_time = 0
if (late_time > 235000):
    diff = late_time
    late_time = 235000
'''
early_time = 000000
late_time = 240000
diff = 0
print("Time is: " + str(early_time) + " to " + str(late_time))
print()


file = open(dector_filename,'r')

debug_count = 0

for line in file:
    columns = line.split()

    #if (int(columns[1]) >= early_time and int(columns[1]) <= late_time):
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

            if (int(columns[1]) >= early_time and int(columns[1]) <= late_time):
                lv0rate_time_sensitive.append(float(columns[3]))
                hitdetnum_time_sensitive.append(int(columns[2]))
                hhmmss_time_sensitive.append(int(columns[1]))

print()
print("Found " + str(debug_count) + " data points for sensors")

file.close()

#open and parse lighting file
file = open(lightning_filename,'r')

debug_count = 0

for line in file:
    columns = line.split()

    temp = columns[1].split(":")
    hours = int(temp[0])
    minutes = int(temp[1])
    seconds = float(temp[2])
    time = hours*10000 + minutes*100 + seconds

    if(time >= early_time and time <= late_time):
        debug_count += 1
        l_date.append(columns[0])
        l_time.append(columns[1])
        l_lat.append(columns[2])
        l_long.append(columns[3])
        l_peakcurrent.append(float(columns[4]))
        l_type.append(columns[5])

print("Found " + str(debug_count) + " data points for lightning")

file.close()

def Time_Table_10():

    times = []
    time = -10000
    for j in range(24):
        time = time + 10000
        for i in range(6):
            times.append(time)
            time = time + 1000
        time = time - 6000

    return times

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-==-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+  Set Data as Readable  +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-==-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

#-----------------------------------------------------Setting-the-det-num--------------------------------------------------------
'''
TGF_x = []
TGF_y = []

print("Getting Det number")

if (len(TGF_center_sensor) > 0):
    if all_day:
        int_det = int(TGF_center_sensor[TGF_number])
        print("All day? Well... I set it to: " + str(TGF_center_sensor[TGF_number]))
    else:
        int_det = int(TGF_center_sensor[TGF_number])
    for i in range(len(tasdnum[0])):
        if (int(TGF_center_sensor[TGF_number]) == int(tasdnum[0][i])):
            TGF_x.append(tasdx[i])
            TGF_y.append(tasdy[i])
            print("Got it")
else:
    int_det = default_sensor
    print("No TGF event?")
'''
#-----------------------------------------------------Easy-use-for-time--------------------------------------------------------
#will create a list called "times" that holds a unique values for each time
'''
times = [hhmmss_time_sensitive[0]]

print()
print("Making easy time table")

for i in range(len(hhmmss_time_sensitive) - 1):
    if (hhmmss_time_sensitive[i] != hhmmss_time_sensitive[i + 1]):
        times.append(hhmmss_time_sensitive[i + 1])

print("Done " + str(len(times)) + " times")
'''
time_table = Time_Table_10()
times = []

print()
print("Making easy time table")

for time in time_table:
    if (time >= early_time and time <= late_time):
        times.append(time)

print("Done " + str(len(times)) + " times")



#-----------------------------------------------Finding-the-x,y-for-each-sensor--------------------------------------------------
s_datax = []
s_datay = []
debug_count = 0
debug_count_2 = 0
flag = 0

print()
print("Making det numbers plottable coordinates")

for i in range(len(hitdetnum_time_sensitive)):
    for j in range(len(tasdnum[0])):
        if (hitdetnum_time_sensitive[i] == tasdnum[0][j]):
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

print()
print("Fixing NLDN data")

for i in range(len(l_peakcurrent)):
    temp = l_time[i].split(":")
    hours = int(temp[0])
    minutes = int(temp[1])
    seconds = float(temp[2])
    l_time_per_hour.append(hours + minutes / 60 + seconds / 3600)
    debug_count += 1

print("Fixed " + str(debug_count) + " NLDN time data points")

#---------------------------------------------Changing-lighting-placement-data-----------------------------------------------------
l_data_xy = [[None, None]]
lighting_data_place = []
debug_count = 0

print()
print("Making NLDN into plottable coordinates")

for i in range(len(times)):
    for j in range(len(l_time_per_hour)):
        hours = int(times[i] / 10000)
        minutes = int(times[i] / 100) - (hours * 100)
        seconds = times[i] - (hours * 10000) - (minutes * 100)
        time = float(hours + minutes / 60 + seconds / 3600)
        if (l_time_per_hour[j] <= time + .16666667):
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
flag = False

print()
print("Finding rates of change")

for i in range(len(hitdetnum_time_sensitive)):
    for j in range(i + 1, len(hitdetnum_time_sensitive)):
        if (hitdetnum_time_sensitive[i] == hitdetnum_time_sensitive[j]):
            sensor_data_level_holder.append((lv0rate_time_sensitive[j] - lv0rate_time_sensitive[i]) * 100 / lv0rate_time_sensitive[i])
            debug_count += 1
            flag = True
            break
    if (not flag):
        sensor_data_level_holder.append(0)
        debug_count += 1
    flag = False

extra_null_points = 1000

for i in range(extra_null_points): #dirty way to fix this array for not having enough points at the end of the cycle
    sensor_data_level_holder.append(0) #(for rate of change, take this one and next one, but at end of line there is no next one)

print("Made " + str(debug_count) + " + " + str(extra_null_points) + " sensor data points into rates")

#-------------------------------------------------Finding-dectors-for-histo---------------------------------------------------
'''
print()
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
'''

#-------------------------------------------------Finding-data-for-histo----------------------------------------------------
NE_dets_str = ['1417', '1418', '1419', '1420', '1421', '1422', '1517', '1518', '1520', '1521', '1522', '1618', '2219', '1221', '1321', '1320', '1220', '1322', '1222', '1223', '1424', '1425', '1325', '1225', '1224', '1324', '2122', '1620', '1621', '1722', '2120', '2021', '1921', '2020', '1718', '1617', '1516', '1616', '1716', '1717', '1817', '1816', '1719', '1819', '1919', '2019', '2119', '2118', '2018', '1918', '1217', '1216', '1215', '1415', '1315', '1316', '1317', '1319', '1219', '1925', '2024', '1924', '1923', '1824', '1724', '1624', '1524', '1723', '1623', '1523', '1423', '1323', '1526', '1626', '1726', '1826', '1825', '1725', '1625', '1525', '1426', '1226', '1218', '1818', '1917', '1820', '1720', '1721', '1318', '2315', '2316', '2117', '2017', '2016', '1915', '2015', '2116', '2216', '2115', '2317', '2217', '2218', '2220', '2215', '2123', '2022', '1823', '1822', '1922', '1622', '1920', '1821', '1326', '1715', '1916', '1815', '1416', '1515', '1615', '2023', '1519', '1427', '1528', '1527', '1627', '1727', '1827', '1628', '1728', '1828', '2025', '1927', '1926', '1619', '2121', '1327', '1428', '4444']
NW_dets_str = ['1018', '0918', '0818', '0718', '0618', '0518', '0418', '0318', '0419', '0519', '0619', '0819', '0920', '0820', '0720', '0620', '0520', '0621', '0721', '0821', '0921', '1021', '1121', '1120', '1020', '1122', '1022', '0922', '0822', '0722', '0823', '0923', '1023', '1123', '1125', '1025', '0924', '1024', '1124', '1017', '1016', '1015', '1115', '0817', '0816', '0815', '0915', '0916', '0917', '0717', '0716', '0715', '0615', '0616', '0617', '1119', '1019', '0919', '0719', '0517', '0417', '0317', '0217', '0116', '0216', '0316', '0416', '0516', '0515', '0415', '0315', '0115', '0215', '1126', '1118', '1117', '1116']
SE_dets_str = ['1908', '2110', '2312', '1214', '1314', '1313', '1514', '1414', '1701', '1801', '1902', '1802', '1702', '1602', '1502', '1504', '1604', '1704', '1804', '1904', '2004', '1903', '1803', '1703', '1603', '1503', '1601', '1501', '1301', '2207', '2307', '2408', '2308', '2309', '2409', '2410', '2411', '1311', '1312', '1412', '1309', '1409', '1510', '1511', '1512', '1411', '1310', '1410', '1308', '1307', '1407', '1507', '1406', '1506', '1606', '1607', '1608', '1609', '1508', '1408', '2010', '2111', '2112', '2012', '1912', '1712', '1612', '1611', '1710', '1711', '1811', '1911', '2011', '1910', '1810', '1914', '2014', '2114', '2214', '2212', '1306', '1505', '1605', '1705', '1305', '1303', '1513', '1614', '1714', '1814', '1813', '1913', '2113', '2213', '2313', '2211', '2412', '2311', '2310', '2210', '2107', '2006', '2005', '2105', '2106', '2206', '1808', '1708', '1709', '1809', '1909', '1907', '1906', '1905', '1304', '1805', '1706', '1707', '1807', '1806', '2007', '2008', '2009', '2109', '2108', '2209', '1202', '1302', '1401', '1402', '1403', '1404', '1405', '2314', '1610', '1509', '1413', '1613', '1713', '1812', '2013', '2208', '2420', '2421']
SW_dets_str = ['1014', '1013', '1113', '1112', '1012', '1011', '1111', '1114', '0814', '0813', '0812', '0811', '0810', '0809', '1010', '0910', '0911', '0912', '0913', '0914', '0714', '0614', '0613', '0713', '0712', '0711', '0710', '0709', '0708', '0608', '0609', '0610', '0611', '0612', '1213', '1212', '0314', '0214', '0114', '0113', '0112', '0111', '0211', '0311', '0411', '0511', '0512', '0412', '0312', '0212', '0213', '0313', '0413', '0513', '0514', '0414', '0107', '0305', '0206', '0306', '0406', '0607', '0507', '0407', '0307', '0207', '0108', '0208', '0308', '0408', '0508', '0509', '0409', '0309', '0209', '0109', '0110', '0210', '0310', '0410', '0510', '0803', '0703', '0603', '0503', '0404', '0504', '0604', '0704', '0804', '0705', '0605', '0505', '0405', '0506', '0606', '0706', '1201', '1101', '1001', '1002', '0802', '0902', '0901', '0801', '0701', '0602', '0702', '1209', '1110', '1210', '1211', '0806', '0906', '1006', '1106', '1206', '1009', '1109', '1208', '1108', '1008', '0908', '0808', '0707', '0807', '0907', '1007', '1107', '1207', '0909', '1205', '1105', '1005', '0905', '0805', '0904', '0903', '1003', '1103', '1203', '1204', '1104', '1004', '1102', '0205', '0304', '0403', '0502', '0601', '0106']
NE_dets = []
NW_dets = []
SE_dets = []
SW_dets = []
for det in NE_dets_str:
    NE_dets.append(int(det))
for det in NW_dets_str:
    NW_dets.append(int(det))
for det in SE_dets_str:
    SE_dets.append(int(det))
for det in SW_dets_str:
    SW_dets.append(int(det))
NE = []
NW = []
SE = []
SW = []
NW_hits = 0
NE_hits = 0
SW_hits = 0
SE_hits = 0
lv0rate = 0
NW_lv0rate_total = 0
NE_lv0rate_total = 0
SW_lv0rate_total = 0
SE_lv0rate_total = 0
per_hour_time = []

print("Finding data for histo...")
for time in time_table:
    per_hour_time.append(int(time/10000) + (int(time/100) % 100) / 60 + ((time % 100) / 3600))

for time in time_table:

    for i in range(len(s_lv0rate)):
        if (time == s_hhmmss[i]):
            if s_hitdetnum[i] in NW_dets:
                NW_lv0rate_total = NW_lv0rate_total + s_lv0rate[i]
                NW_hits += 1
            if s_hitdetnum[i] in NE_dets:
                NE_lv0rate_total = NE_lv0rate_total + s_lv0rate[i]
                NE_hits += 1
            if s_hitdetnum[i] in SW_dets:
                SW_lv0rate_total = SW_lv0rate_total + s_lv0rate[i]
                SW_hits += 1
            if s_hitdetnum[i] in SE_dets:
                SE_lv0rate_total = SE_lv0rate_total + s_lv0rate[i]
                SE_hits += 1

    if NW_hits == 0:
        NW.append(None)
    else:
        NW.append(NW_lv0rate_total / NW_hits)

    if NE_hits == 0:
        NE.append(None)
    else:
        NE.append(NE_lv0rate_total / NE_hits)

    if SW_hits == 0:
        SW.append(None)
    else:
        SW.append(SW_lv0rate_total / SW_hits)

    if SE_hits == 0:
        SE.append(None)
    else:
        SE.append(SE_lv0rate_total / SE_hits)

    NW_lv0rate_total = 0
    NW_hits = 0
    NE_lv0rate_total = 0
    NE_hits = 0
    SW_lv0rate_total = 0
    SW_hits = 0
    SE_lv0rate_total = 0
    SE_hits = 0
''' not working bc of none type and >
min_lv0_rate = min(NW)
min = min(NE)
if min < min_lv0_rate:
    min_lv0rate = min
min = min(SE)
if min < min_lv0_rate:
    min_lv0rate = min
min = min(SW)
if min < min_lv0_rate:
    min_lv0rate = min

max_lv0_rate = max(NW)
max = max(NE)
if max > max_lv0_rate:
    max_lv0_rate = max
max = max(SE)
if max > max_lv0_rate:
    max_lv0_rate = max
max = max(SW)
if max > max_lv0_rate:
    max_lv0_rate = max
'''
min_lv0_rate = 690
max_lv0_rate = 750
#-------------------------------------------------------Fixing-TGF-times--------------------------------------------------------
'''
TGF_fixed_time = []

for time in TGF_time:
    temp = time.split(":")
    hours = int(temp[0])
    minutes = int(temp[1])
    seconds = float(temp[2])
    TGF_fixed_time.append(hours + (minutes / 60) + (seconds / 3600))

TGF_fixed_time.append(None)
TGF_fixed_time.append(None)
TGF_fixed_time.append(None)
'''
#--------------------------------------------Putting-times-in-easy-to-read-matrices--------------------------------------------
sensor_data_place = []
sensor_data_level = []
hit_x_y = []
hit_c = []

print("Making data readable...")

for i in range(len(times)):
    for j in range(len(hhmmss_time_sensitive)):
        if (int(hhmmss_time_sensitive[j]) == int(times[i])):
            hit_x_y.append([s_datax[j], s_datay[j]])
            hit_c.append(sensor_data_level_holder[j])

    sensor_data_place.append(hit_x_y)
    sensor_data_level.append(hit_c)
    hit_x_y = []
    hit_c = []

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+  Animation  +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|-=-=-=-=-=-=-|-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

print()
print("Building...")

def init():
    lp_time_counter.set_data([], [])
    lp_time_counter1.set_data([], [])
    lp_time_counter2.set_data([], [])
    lp_time_counter3.set_data([], [])
    lp_time_counter4.set_data([], [])
    sp_sensor_readings.set_offsets([[], []])
    sp_lightning_readings.set_offsets([[], []])
    return listplots

def update(frame):
    print("NE")
    print(NE[frame])
    print("NW")
    print(NW[frame])
    print("SE")
    print(SE[frame])
    print("SW")
    print(SW[frame])
    print()

    x = int(early_time/10000) + (int(early_time/100) % 100) / 60 + ((early_time % 100) / 3600) + (frame * 1/6) % (int(late_time/10000) - int(early_time/10000) + diff)
    y = np.linspace(-300, 1000, 250) #time counter function

    lp_time_counter.set_data(x, y)

    lp_time_counter1.set_data(x, y)
    lp_time_counter2.set_data(x, y)
    lp_time_counter3.set_data(x, y)
    lp_time_counter4.set_data(x, y)

    sp_sensor_readings.set_offsets(sensor_data_place[frame])
    sp_lightning_readings.set_offsets(lighting_data_place[frame])

    sp_sensor_readings.set_array(np.asarray(sensor_data_level[frame]))

    return listplots

print(" Figure") #debug
fig = plt.figure(constrained_layout=False)
'''
#set the title
if all_day:
    title = "On " + str(date) + " at "
    for i in range(len(TGF_time)):
        temp = TGF_time[i].split(".")
        title = title + str(temp[0]) + " | " + str(TGF_center_sensor[i]) + ", "
    title = title.rstrip()
    title = title.rstrip(",")
else:
    title = "On " +str(date) + " at " + str(TGF_time[TGF_number]) + " | " + str(TGF_center_sensor[TGF_number])
'''
title = "On " + str(date) + " at "
for i in range(len(TGF_time)):
    temp = TGF_time[i].split(".")
    title = title + str(temp[0]) + " | " + str(TGF_center_sensor[i]) + ", "
title = title.rstrip()
title = title.rstrip(",")

fig.suptitle(title, fontsize=10)

cmap = mpl.colors.ListedColormap(["blue", "#00FFFF", "green", "#FFa500", "red"])
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

gs1 = fig.add_gridspec(5, 3, left=0.08, right=0.48, top=.92, bottom=.08, wspace=1, hspace=0.5)

plt.rc('xtick', labelsize = 6)
plt.rc('ytick', labelsize = 6)

print(" Sensors") #debug
j_ax1 = fig.add_subplot(gs1[:3, :3]) #setting subplot location
j_ax1.set_xlim(-20, 20) #limits
j_ax1.set_ylim(-23, 18)
lp_WE, = j_ax1.plot([-0.8, -0.8], [-23, 18], lw=1, c='black')
lp_NS, = j_ax1.plot([20, -20], [-2.3, -2.3], lw=1, c='black')
#sp_TGF = j_ax1.scatter(TGF_x, TGF_y, c="black", s=5000, marker=".")
sp_sensors = j_ax1.scatter(tasdx, tasdy, c='yellow', s=size_of_sensors, marker='.') #this is for placing the general sensors (the yellow dots)
sp_sensor_readings = j_ax1.scatter([], [], c=[], s=size_of_sensor_data, cmap=cmap, norm=norm, marker='s', vmin = -1, vmax = 1) #this is for showing the sensor readings
sp_lightning_readings = j_ax1.scatter([], [], c='purple', s=size_of_lightning, marker='+') #this is for showing the nldn readings (the purple +'s)

plt.colorbar(sp_sensor_readings, cmap=cmap, norm=norm)

print(" NLDN") #debug
j_ax2 = fig.add_subplot(gs1[3:, :3])
j_ax2.grid(True)
j_ax2.set_xlim(int(early_time/10000) + (int(early_time/100) % 100) / 60 + ((early_time % 100) / 3600), int(late_time/10000) + (int(late_time/100) % 100) / 60 + ((late_time % 100) / 3600))
j_ax2.set_ylim(-250,250)
#j_ax2.set_xticks((0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24))
j_ax2.set_ylabel("Peak Current")
j_ax2.set_xlabel("Time")
j_ax2.set_yticks((-250, -200, -150, -100, -50, 0, 50, 100, 150, 200, 250))
sp_lightning_level = j_ax2.scatter(l_time_per_hour, l_peakcurrent, c='purple', s=size_of_lightning/2, marker='+')   #input np.arrays of lighting data
lp_time_counter, = j_ax2.plot([], [], lw=1, c='blue') #this is for iteratoring along the time on the bottom graph
'''
lp_TGF_NLDN_0 = j_ax2.plot([TGF_fixed_time[0], TGF_fixed_time[0]],[-250,250],lw=1, c='orange')
lp_TGF_NLDN_1 = j_ax2.plot([TGF_fixed_time[1], TGF_fixed_time[1]],[-250,250],lw=1, c='orange')
lp_TGF_NLDN_2 = j_ax2.plot([TGF_fixed_time[2], TGF_fixed_time[2]],[-250,250],lw=1, c='orange')
'''

print(" Histos") #debug
gs2 = fig.add_gridspec(2, 2, left=0.53, right=0.98, wspace=0.3, hspace=0.3)

NW_ax = fig.add_subplot(gs2[0,0])
NW_ax.set_ylim(min_lv0_rate, max_lv0_rate)
NW_ax.set_xlim(0,24)
lp_time_counter1, = NW_ax.plot([], [], lw=1, c='blue')
NW_ax.plot(per_hour_time, NW, lw=1, c='green')

NE_ax = fig.add_subplot(gs2[0,1])
NE_ax.set_ylim(min_lv0_rate, max_lv0_rate)
NE_ax.set_xlim(0,24)
lp_time_counter2, = NE_ax.plot([], [], lw=1, c='blue')
NE_ax.plot(per_hour_time, NE, lw=1, c='green')

SE_ax = fig.add_subplot(gs2[1,0])
SE_ax.set_ylim(min_lv0_rate, max_lv0_rate)
SE_ax.set_xlim(0,24)
lp_time_counter3, = SE_ax.plot([], [], lw=1, c='blue')
SE_ax.plot(per_hour_time, SE, lw=1, c='green')

SW_ax = fig.add_subplot(gs2[1,1])
SW_ax.set_ylim(min_lv0_rate, max_lv0_rate)
SW_ax.set_xlim(0,24)
lp_time_counter4, = SW_ax.plot([], [], lw=1, c='blue')
SW_ax.plot(per_hour_time, SW, lw=1, c='green')

listplots = [sp_sensor_readings, sp_lightning_readings, lp_time_counter, lp_time_counter1, lp_time_counter2, lp_time_counter3, lp_time_counter4]


print(" Animation")
anim = animation.FuncAnimation(fig, update, init_func=init, interval=anispeed, blit=True, repeat=True, frames=len(sensor_data_place))

print("Done")

print()
save = str(input("Save? [y/n] "))
while (save != "y" and save != "n"):
    save = str(input("Invalid response. Save? [y/n] "))

if (save == "y"):
    print("Saving...")
    HTML(anim.to_html5_video())
    place = "AvgMovies/" + str(date)
    anim.save(place + "/AllDay.mp4", fps=1, writer="ffmpeg", dpi=1000, bitrate=5000)
    '''
    if all_day:
        anim.save(place + "/AllDay.mp4", fps=1, writer="ffmpeg", dpi=1000, bitrate=5000)
    else:
        anim.save(place + "/TGFnum" + str(TGF_number + 1) + ".mp4", fps=1, writer="ffmpeg", dpi=1000, bitrate=5000)
    '''
plt.show()
