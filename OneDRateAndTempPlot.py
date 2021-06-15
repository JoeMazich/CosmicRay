import os
from datetime import *

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

inputdate = input('What date? ')
det1 = input('Det 1? ')
det2 = input('Det 2? ')
det3 = input('Det 3? ')

earlytime  = '080000'
latetime   = '235000'
markedtime = '084000'

a = '080000'
b = '100000'
c = '120000'
d = '180000'
e = '235000'

file = open("DataDates/temp/" + inputdate + "/L0L1.txt", 'r')
l01, l02, l03, temp1, temp2, temp3 = [], [], [], [], [], []
times1, times2, times3 = [], [], []

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

markedtime = datetime.combine(Date_P2D(inputdate), (Time_P2D(markedtime)))

a = datetime.combine(Date_P2D(inputdate), (Time_P2D(a)))
b = datetime.combine(Date_P2D(inputdate), (Time_P2D(b)))
c = datetime.combine(Date_P2D(inputdate), (Time_P2D(c)))
d = datetime.combine(Date_P2D(inputdate), (Time_P2D(d)))
e = datetime.combine(Date_P2D(inputdate), (Time_P2D(e)))

for line in file:
    columns = line.split()

    if (int(columns[1]) >= int(earlytime)) and (int(columns[1]) <= int(latetime)):
        if (columns[2] == det1):
            l01.append(float(columns[3]))
            temp1.append(float(columns[8]))
            times1.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
        elif (columns[2] == det2):
            l02.append(float(columns[3]))
            temp2.append(float(columns[8]))
            times2.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
        elif (columns[2] == det3):
            l03.append(float(columns[3]))
            temp3.append(float(columns[8]))
            times3.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))

file.close()

fig = plt.figure(constrained_layout=False)


gs = fig.add_gridspec(2, 3, left=0.09, right=0.91, top=.87, bottom=0.09, wspace=0.4, hspace=0.2)
fig.suptitle(inputdate)

l01ax = fig.add_subplot(gs[0, 0])
l01ax.set_title(det1)
l01ax.set_xticks([])
l01ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l01ax.plot(times1, l01)
l01ax.plot([markedtime, markedtime], [0, 10000])
l01ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
l01ax.set_ylim([720, 750])

temp1ax = fig.add_subplot(gs[1, 0])
temp1ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp1ax.plot(times1, temp1)
temp1ax.plot([markedtime, markedtime], [0, 10000])
temp1ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
temp1ax.set_xticks([a,b,c,d,e])
temp1ax.set_ylim([16, 21])

l02ax = fig.add_subplot(gs[0, 1])
l02ax.set_title(det2)
l02ax.set_xticks([])
l02ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l02ax.plot(times2, l02)
l02ax.plot([markedtime, markedtime], [0, 10000])
l02ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
l02ax.set_ylim([720, 750])

temp2ax = fig.add_subplot(gs[1, 1])
temp2ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp2ax.plot(times2, temp2)
temp2ax.plot([markedtime, markedtime], [0, 10000])
temp2ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
temp2ax.set_xticks([a,b,c,d,e])
temp2ax.set_ylim([16, 21])

l03ax = fig.add_subplot(gs[0, 2])
l03ax.set_title(det3)
l03ax.set_xticks([])
l03ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l03ax.plot(times3, l03)
l03ax.plot([markedtime, markedtime], [0, 10000])
l03ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
l03ax.set_ylim([720, 750])

temp3ax = fig.add_subplot(gs[1, 2])
temp3ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp3ax.plot(times3, temp3)
temp3ax.plot([markedtime, markedtime], [0, 10000])
temp3ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
temp3ax.set_xticks([a,b,c,d,e])
temp3ax.set_ylim([16, 21])

plt.show()
