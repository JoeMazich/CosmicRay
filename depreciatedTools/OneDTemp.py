import os
from datetime import *
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

inputdate = input('What date? ')
det1 = input('1? ')
det2 = input('2? ')
det3 = input('3? ')

earlytime  = '060000'
latetime   = '110000'
markedtime = '080000'

a = '060000'
b = '070000'
c = '080000'
d = '090000'
e = '100000'
f = '110000'


file = open("DataDates/" + inputdate + "/L0L1.txt", 'r')
l01, l02, l03, temp1, temp2, temp3 = [], [], [], [], [], []
yerr1, yerr2, yerr3 = [], [], []
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
f = datetime.combine(Date_P2D(inputdate), (Time_P2D(f)))

for line in file:
    columns = line.split()

    if (int(columns[1]) >= int(earlytime)) and (int(columns[1]) <= int(latetime)):
        if (columns[2] == det1):
            l01.append(float(columns[3]))
            temp1.append(float(columns[8]))
            times1.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
            yerr1.append( ( 1 / math.sqrt( float(columns[3]) * 60 * 10 ) ) * float(columns[3]) )

        elif (columns[2] == det2):
            l02.append(float(columns[3]))
            temp2.append(float(columns[8]))
            times2.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
            yerr2.append( ( 1 / math.sqrt( float(columns[3]) * 60 * 10 ) ) * float(columns[3]) )

        elif (columns[2] == det3):
            l03.append(float(columns[3]))
            temp3.append(float(columns[8]))
            times3.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
            yerr3.append( ( 1 / math.sqrt( float(columns[3]) * 60 * 10 ) ) * float(columns[3]) )

file.close()

fig = plt.figure(constrained_layout=False)

gs = fig.add_gridspec(2, 3, left=0.09, right=0.91, top=.87, bottom=0.09, wspace=0.2, hspace=0.2)
#fig.suptitle("EAS Rate vs Tempature")
print('yerr1', min(yerr1), max(yerr1))
print('yerr2', min(yerr2), max(yerr2))
print('yerr3', min(yerr3), max(yerr3))

l01ax = fig.add_subplot(gs[0, 0])
l01ax.set_title(det1)
l01ax.set_xticks([])
l01ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l01ax.errorbar(times1, l01, yerr=yerr1, zorder=2, capsize=1.5, elinewidth=1)
l01ax.plot([markedtime, markedtime], [0, 10000], zorder=1)
l01ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
l01ax.set_ylim([721, 744])
l01ax.set_ylabel('Level 0 Rate (Hz)')

temp1ax = fig.add_subplot(gs[1, 0])
temp1ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp1ax.plot(times1, temp1)
temp1ax.plot([markedtime, markedtime], [0, 10000])
temp1ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
temp1ax.set_xticks([a,b,c,d,e,f])
temp1ax.set_ylim([16, 22])
temp1ax.set_xlabel('Time (UTC)')
temp1ax.set_ylabel('Tempature (C)')

l02ax = fig.add_subplot(gs[0, 1])
l02ax.set_title(det2)
l02ax.set_xticks([])
l02ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l02ax.errorbar(times2, l02, yerr=yerr2, zorder=2, capsize=1.5, elinewidth=0.8)
l02ax.plot([markedtime, markedtime], [0, 10000], zorder=1)
l02ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
l02ax.set_ylim([721, 744])

temp2ax = fig.add_subplot(gs[1, 1])
temp2ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp2ax.plot(times2, temp2)
temp2ax.plot([markedtime, markedtime], [0, 10000])
temp2ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
temp2ax.set_xticks([a,b,c,d,e,f])
temp2ax.set_ylim([16, 22])
temp2ax.set_xlabel('Time (UTC)')

l03ax = fig.add_subplot(gs[0, 2])
l03ax.set_title(det2)
l03ax.set_xticks([])
l03ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l03ax.errorbar(times3, l03, yerr=yerr3, zorder=2, capsize=1.5, elinewidth=0.8)
l03ax.plot([markedtime, markedtime], [0, 10000], zorder=1)
l03ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
l03ax.set_ylim([721, 744])

temp3ax = fig.add_subplot(gs[1, 2])
temp3ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp3ax.plot(times3, temp3)
temp3ax.plot([markedtime, markedtime], [0, 10000])
temp3ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime)))])
temp3ax.set_xticks([a,b,c,d,e,f])
temp3ax.set_ylim([16, 22])
temp3ax.set_xlabel('Time (UTC)')


plt.show()
