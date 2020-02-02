import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from taTools import *

#set filename
filename = raw_input("What day do you want to view? (MMDD) ")
filename = filename + ".dat"
#filename = "0514.dat"

min_size = 11
max_size = 50

anispeed = 250

fcount = 144

#init
tasdnum,tasdx,tasdy,tasdz =[],[],[],[]
tasdxyz(tasdnum,tasdx,tasdy,tasdz)

tasdlat,tasdlon,tasdalt = [],[],[]
tasdgps(tasdlat,tasdlon,tasdalt)

YYMMDD = []
hhmmss = []
Hitdetnum = []
lv0rate = []
lv1rate = []
warn = []
dontuse = []
quality = []

hitx = []
hity = []
Rnglv0rate = []

#open file
file = open(filename,'r')

for line in file:
    columns = line.split()

    YYMMDD.append(int(columns[0]))
    hhmmss.append(int(columns[1]))
    Hitdetnum.append(int(columns[2]))
    lv0rate.append(float(columns[3]))
    lv1rate.append(float(columns[4]))
    dontuse.append(int(columns[5]))
    warn.append(int(columns[6]))
    quality.append(int(columns[7]))

#close file
file.close()

#get each unique time in order
times = [hhmmss[0]]

for i in range(len(hhmmss) - 1):
    if (hhmmss[i] != hhmmss[i + 1]):
        times.append(hhmmss[i + 1])

#plot and animation setup
fig = plt.figure()
ax = fig.add_subplot(111, xlim = (-20,20), ylim = (-23,18))
p = ax.scatter([], [], c=[], s=50, cmap="jet", marker = 's', vmin = 700, vmax = 780)

ax.grid(True)

ax.scatter(tasdx,tasdy, c='r', s = 10, marker='s')

#for defining the size in relation of the quality
minqual = min(quality)
maxqual = max(quality)

#collecting generally needed data
datax = []
datay = []

for i in range(len(Hitdetnum)):
    for j in range(len(tasdnum[0])):
        if (Hitdetnum[i] == tasdnum[0][j]):
            datax.append(tasdx[j])
            datay.append(tasdy[j])


def animate(frame):
    t = frame % 144

    hit_x = []
    hit_y = []
    hit_c = []
    hit_s = []
    hit_t = []

    for i in range(len(hhmmss)):
        if (hhmmss[i] == int(times[t]) and dontuse[i] == 0): #and warn[i] == 0
            hit_x.append(datax[i])
            hit_y.append(datay[i])
            hit_c.append(lv0rate[i])

            hit_s.append((((quality[i] - minqual) / (maxqual - minqual)) * (min_size - max_size) + max_size))
            hit_t.append(hhmmss[i])

    hit_x_y = np.array([[ hit_x[0] ,  hit_y[0] ]])

    for i in range(1, len(hit_x)):
        update = np.array([[ hit_x[i] , hit_y[i] ]])
        hit_x_y = np.append(hit_x_y, update, axis = 0)

    colors = np.asarray(hit_c)
    #sizes = np.asarray(hit_s)
    time = np.asarray(hit_t)

    p.set_offsets(hit_x_y)
    p.set_array(colors)
    #p.set_sizes(sizes)
    p.set_label(time)

    return p,

anim = animation.FuncAnimation(fig, animate, frames = fcount, interval = anispeed, blit = True)

fig.colorbar(p)
plt.show()
