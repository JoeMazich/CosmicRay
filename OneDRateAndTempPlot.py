import os
from datetime import *

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

inputdate = input('What date? ')
det = input('What det? ')

earlytime = 80000
latetime  = 100000

file = open("DataDates/temp/" + inputdate + "/L0L1.txt", 'r')
l0, temp = [], []
times = []

def Date_P2D(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return date(year, month, day)

def Time_P2D(plain_time):
    hour = int(plain_time[0:2])
    min = int(plain_time[2:4])
    sec = int(plain_time[4:6])
    return time(hour, min, sec)

for line in file:
    columns = line.split()

    if (columns[2] == det) and (int(columns[1]) > earlytime) and (int(columns[1]) < latetime):
        l0.append(float(columns[3]))
        temp.append(float(columns[8]))
        times.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))

file.close()


fig = plt.figure(constrained_layout=False)

gs = fig.add_gridspec(2, 1, left=0.09, right=0.91, top=.87, bottom=0.09, wspace=0.4, hspace=0.5)

l0ax = fig.add_subplot(gs[0, 0])
l0ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l0ax.plot(times, l0)

tempax = fig.add_subplot(gs[1, 0])
tempax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
tempax.plot(times, temp)



plt.show()
