import os
from datetime import *
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

inputdate = '140927'#input('What date? ')
#det1 = input('Excess 1? ')
det2 = input('Deficit 2? ')

earlytime_e  = '160000'
latetime_e   = '210000'
markedtime_e = '191000'

a_e = '160000'
b_e = '170000'
c_e = '180000'
d_e = '190000'
e_e = '200000'
f_e = '210000'

earlytime_d  = '060000'
latetime_d   = '110000'
markedtime_d = '080000'

a_d = '060000'
b_d = '070000'
c_d = '080000'
d_d = '090000'
e_d = '100000'
f_d = '110000'


file = open("DataDates/" + inputdate + "/L0L1.txt", 'r')
l01, l02, l03, temp1, temp2, temp3 = [], [], [], [], [], []
yerr1, yerr2 = [], []
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
f_e = datetime.combine(Date_P2D(inputdate), (Time_P2D(f_e)))

a_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(a_d)))
b_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(b_d)))
c_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(c_d)))
d_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(d_d)))
e_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(e_d)))
f_d = datetime.combine(Date_P2D(inputdate), (Time_P2D(f_d)))

for line in file:
    columns = line.split()

    '''if (columns[2] == det1) and (int(columns[1]) >= int(earlytime_e)) and (int(columns[1]) <= int(latetime_e)):
        l01.append(float(columns[3]))
        temp1.append(float(columns[8]))
        print(columns[8], '1')
        times1.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
        yerr1.append( ( 1 / math.sqrt( float(columns[3]) * 60 * 10 ) ) * float(columns[3]) )'''

    if (columns[2] == det2) and (int(columns[1]) >= int(earlytime_d)) and (int(columns[1]) <= int(latetime_d)):
        l02.append(float(columns[3]))
        temp2.append(float(columns[8]))
        #print(columns[8], '2')
        times2.append(datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))))
        yerr2.append( ( 1 / math.sqrt( float(columns[3]) * 60 * 10 ) ) * float(columns[3]) )

file.close()

fig = plt.figure(constrained_layout=False)

gs = fig.add_gridspec(2, 1, left=0.09, right=0.91, top=.87, bottom=0.09, wspace=0.2, hspace=0.2)
#fig.suptitle("EAS Rate vs Tempature")
#print('yerr1', min(yerr1), max(yerr1))
print('yerr2', min(yerr2), max(yerr2))

'''l01ax = fig.add_subplot(gs[0, 1])
l01ax.set_title(det1)
l01ax.set_xticks([])
l01ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l01ax.errorbar(times1, l01, yerr=yerr1, zorder=2, capsize=1.5, elinewidth=1)
l01ax.plot([markedtime_e, markedtime_e], [0, 10000], zorder=1)
l01ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_e))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_e)))])
l01ax.set_ylim([721, 744])'''
#l01ax.set_yticks([727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744])

'''temp1ax = fig.add_subplot(gs[0, 0])
temp1ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp1ax.plot(times1, temp1)
temp1ax.plot([markedtime_e, markedtime_e], [0, 10000])
temp1ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_e))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_e)))])
temp1ax.set_xticks([a_e,b_e,c_e,d_e,e_e,f_e])
temp1ax.set_ylim([16, 22])
temp1ax.set_xlabel('Time (UTC)')'''

l02ax = fig.add_subplot(gs[0, 0])
l02ax.set_title(det2)
l02ax.set_xticks([])
l02ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
l02ax.errorbar(times2, l02, yerr=yerr2, zorder=2, capsize=1.5, elinewidth=0.8)
l02ax.plot([markedtime_d, markedtime_d], [0, 10000], zorder=1)
l02ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_d))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_d)))])
l02ax.set_ylim([min(l02) - 2, max(l02) + 2])
#l02ax.set_yticks([727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744])
l02ax.set_ylabel('Level 0 Rate (Hz)')

temp2ax = fig.add_subplot(gs[1, 0])
temp2ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
temp2ax.plot(times2, temp2)
temp2ax.plot([markedtime_d, markedtime_d], [0, 10000])
temp2ax.set_xlim([datetime.combine(Date_P2D(inputdate), (Time_P2D(earlytime_d))), datetime.combine(Date_P2D(inputdate), (Time_P2D(latetime_d)))])
temp2ax.set_xticks([a_d,b_d,c_d,d_d,e_d,f_d])
temp2ax.set_ylim([16, 22])
temp2ax.set_xlabel('Time (UTC)')
temp2ax.set_ylabel('Tempature (C)')

fig.set_size_inches(6.5, 8)

plt.show()

save = input('Save? (Y/n): ')
if (save == 'Y' or save == 'y'):
    fig.savefig(det2 + '.png')
