import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from datetime import *

TEN_MINS = timedelta(minutes=10)
THREE_HOURS = timedelta(hours=3)

filename = input("What date? ")
det = input("What det? ")

temps = []
rates = []

file = open("DataDates/temp/" + filename + "/L0L1.txt", 'r')

def Date_P2D(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return date(year, month, day)

def Time_Table(date):
    time_table = []
    dateAndTime = datetime.combine(Date_P2D(date), time(hour=0, minute=0, second=0))
    time_table.append(dateAndTime)
    for i in range(143):
        dateAndTime += TEN_MINS
        time_table.append(dateAndTime)
    return time_table


for line in file:
    columns = line.split()

    if columns[2] == det:
        temps.append(float(columns[8]))
        rates.append(float(columns[3]))

file.close()

ZeroHour = datetime.combine(Date_P2D(filename), (time(second=0)))

xLabels = []
for i in range(9):
    xLabels.append(ZeroHour + i * THREE_HOURS)

anno_opts = dict(xy=(0.5, 0.9), xycoords='axes fraction', va='center', ha='center')

fig, ax = plt.subplots(nrows=2, ncols=1)
fig.suptitle('Date: ' + filename + ', Detector: ' + det, fontsize=16)

ax[0].plot(Time_Table(filename), temps)
ax[0].set_xticks([])
ax[0].annotate('Tempatures (C)', **anno_opts)

ax[1].plot(Time_Table(filename), rates)
ax[1].set_xticks(xLabels)
ax[1].xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
ax[1].annotate('Level 0 Rates', **anno_opts)

plt.show()
