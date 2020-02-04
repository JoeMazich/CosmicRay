import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from taTools import *
from statistics import mean, median

#--------------------------------Input------------------------------------------
filename = raw_input("What day do you want to view? (MMDD) ")
filename = filename + ".dat"
#-------------------------------------------------------------------------------


#---------------------------------Initalization---------------------------------
anispeed = 25 #speed of animation in ms
fcount = 144 #frames in animation
bot_percent = 5 #bottom percent for determining the color grad
top_percent = 100 - bot_percent

#for lat/long to x,y conversion
tasdnum,tasdx,tasdy,tasdz =[],[],[],[]
tasdxyz(tasdnum,tasdx,tasdy,tasdz)

tasdlat,tasdlon,tasdalt = [],[],[]
tasdgps(tasdlat,tasdlon,tasdalt)

#for lat/long conversion and animation
hit_x = []
hit_y = []
hit_c = []
datax = []
datay = []

#for sensors
YYMMDD = []
hhmmss = []
Hitdetnum = []
lv0rate = []
lv1rate = []
warn = []
dontuse = []
quality = []

#for lighting
l_date = []
l_time = []
l_x = []
l_y = []
l_peakcurrent = []
l_type = []
#-------------------------------------------------------------------------------


#-----------------------------Reading-the-data----------------------------------
#open and parse sensor file
file = open(filename,'r')

for line in file:
    columns = line.split()

    if (int(columns[5]) == 0): #take out dont use
                               #for taking out dontuse: int(columns[5]) == 0
                               #for taking out warns: and int(columns[6]) == 0
        YYMMDD.append(int(columns[0]))
        hhmmss.append(int(columns[1]))
        Hitdetnum.append(int(columns[2]))
        lv0rate.append(float(columns[3]))
        lv1rate.append(float(columns[4]))
        dontuse.append(int(columns[5]))
        warn.append(int(columns[6]))
        quality.append(int(columns[7]))

file.close()

#open and parse lighting file
file = open("nldn.dat",'r')

for line in file:
    columns = line.split()

    l_date.append(columns[0])
    l_time.append(columns[1])
    l_x.append(columns[2])
    l_y.append(columns[3])
    l_peakcurrent.append(columns[4])
    l_type.append(columns[5])

file.close()
#-------------------------------------------------------------------------------


#--------------------------------Statistics-------------------------------------
Q1 = np.percentile(lv0rate, 25, interpolation = 'midpoint')
Q3 = np.percentile(lv0rate, 75, interpolation = 'midpoint')
IQL = Q3 - Q1

#find z score
z_lv0rate = []
mean_lv0 = mean(lv0rate)

for i in range(len(lv0rate)):
    z_lv0rate.append((lv0rate[i] - mean_lv0) / IQL)

QBOT = np.percentile(z_lv0rate, bot_percent, interpolation = 'midpoint')
QTOP = np.percentile(z_lv0rate, top_percent, interpolation = 'midpoint')

#quick check to see if data is good, should be low, less than 10 preferablly
print(QTOP - QBOT)
#-------------------------------------------------------------------------------


#------------------------------Easy-use-for-time--------------------------------
#will create a list called "times" that holds a unique values for each time
times = [hhmmss[0]]

for i in range(len(hhmmss) - 1):
    if (hhmmss[i] != hhmmss[i + 1]):
        times.append(hhmmss[i + 1])
#-------------------------------------------------------------------------------


#-------------------------------Animation-setup---------------------------------
#set the figure
fig = plt.figure()
ax = fig.add_subplot(111, xlim = (-20,20), ylim = (-23,18))
ax.grid(True)

#place all the sensors
ax.scatter(tasdx,tasdy, c='r', s = 10, marker='s')

#initalize the sensor readings
p_s = ax.scatter([], [], c=[], s=50, cmap="jet", marker = 's',\
                                    vmin = QBOT, vmax = QTOP)
#-------------------------------------------------------------------------------


#--------------------------Setting-lat/long-to-x,y------------------------------
for i in range(len(Hitdetnum)):
    for j in range(len(tasdnum[0])):
        if (Hitdetnum[i] == tasdnum[0][j]):
            datax.append(tasdx[j])
            datay.append(tasdy[j])
#-------------------------------------------------------------------------------


def animate(frame):
    #determing the time iterator
    t = frame % 144

    #picking the specific times for data using time array and iterator
    for i in range(len(hhmmss)):
        if (hhmmss[i] == int(times[t])):
            hit_x.append(datax[i])
            hit_y.append(datay[i])
            hit_c.append(z_lv0rate[i])

    #really backwards way of setting up an nparray
    hit_x_y = np.array([[ hit_x[0] ,  hit_y[0] ]])
    for i in range(1, len(hit_x)):
        update = np.array([[ hit_x[i] , hit_y[i] ]])
        hit_x_y = np.append(hit_x_y, update, axis = 0)

    colors = np.asarray(hit_c)

    #set the new data points
    p_s.set_offsets(hit_x_y)
    p_s.set_array(colors)

    return p_s,

anim = animation.FuncAnimation(fig, animate, frames = fcount,\
                interval = anispeed, blit = True)

fig.colorbar(p_s)
plt.show()
