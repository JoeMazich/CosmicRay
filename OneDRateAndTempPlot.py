import os
from datetime import *

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

inputdate = input('What date? ')
det1 = input('Excess 1? ')
det2 = input('Deficit 2? ')

earlytime_e  = '170000'
latetime_e   = '200000'
markedtime_e = '190000'

a_e = '170000'
b_e = '180000'
c_e = '190000'
d_e = '200000'

e_e = '100000'

earlytime_d  = '070000'
latetime_d   = '100000'
markedtime_d = '075000'

a_d = '070000'
b_d = '080000'
c_d = '090000'
d_d = '100000'

e_d = '090000'

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

markedtime_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(markedtime_e)))
markedtime_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(markedtime_d)))

a_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(a_e)))
b_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(b_e)))
c_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(c_e)))
d_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(d_e)))
e_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(e_e)))

a_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(a_d)))
b_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(b_d)))
c_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(c_d)))
d_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(d_d)))
e_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(e_d)))

for line in file:
    columns = line.split()

    if (columns[2] == det1) and (int(columns[1]) >= int(earlytime_e)) and (int(columns[1]) <= int(latetime_e)):
        l01.append(float(columns[3]))
        temp1.append(float(columns[8]))
        times1.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))

    if (columns[2] == det2) and (int(columns[1]) >= int(earlytime_d)) and (int(columns[1]) <= int(latetime_d)):
        l02.append(float(columns[3]))
        temp2.append(float(columns[8]))
        times2.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))

file.close()

fig = plt.figure(constrained_layout=False)

gs = fig.add_gridspec(2, 2, left=0.09, right=0.91, top=.87, bottom=0.09, wspace=0.2, hspace=0.2)
#fig.suptitle("EAS Rate vs Tempature")

l01ax = fig.add_subplot(gs[0, 1])
l01ax.set_title(det1)
l01ax.set_xticks([])
l01ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l01ax.plot(times1, l01)
l01ax.plot([markedtime_e, markedtime_e], [0, 10000])
l01ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_e))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_e)))])
l01ax.set_ylim([727, 742])


temp1ax = fig.add_subplot(gs[1, 1])
temp1ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp1ax.plot(times1, temp1)
temp1ax.plot([markedtime_e, markedtime_e], [0, 10000])
temp1ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_e))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_e)))])
temp1ax.set_xticks([a_e,b_e,c_e,d_e])
temp1ax.set_ylim([16, 22])
temp1ax.set_xlabel('Time (UTC)')

l02ax = fig.add_subplot(gs[0, 0])
l02ax.set_title(det2)
l02ax.set_xticks([])
l02ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l02ax.plot(times2, l02)
l02ax.plot([markedtime_d, markedtime_d], [0, 10000])
l02ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_d))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_d)))])
l02ax.set_ylim([727, 742])
l02ax.set_ylabel('Level 0 Rate (Hz)')

temp2ax = fig.add_subplot(gs[1, 0])
temp2ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp2ax.plot(times2, temp2)
temp2ax.plot([markedtime_d, markedtime_d], [0, 10000])
temp2ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_d))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_d)))])
temp2ax.set_xticks([a_d,b_d,c_d,d_d])
temp2ax.set_ylim([16, 22])
temp2ax.set_xlabel('Time (UTC)')
temp2ax.set_ylabel('Tempature (C)')

plt.show()
