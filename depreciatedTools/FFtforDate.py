from scipy.fft import fft, fftfreq, ifft
import matplotlib.pyplot as plt
import numpy as np
from datetime import *

TEN_MINS = timedelta(minutes=10)

inputdate = input('What date? ')
det = input('What det? ')

file = open("DataDates/temp/" + inputdate + "/L0L1.txt", 'r')
l01 = []

for line in file:
    columns = line.split()
    if (columns[2] == det):
        l01.append(float(columns[3]))
file.close()

def Time_Table(date):
    time_table = []
    dateAndTime = datetime.combine(Date_P2D(date), time(hour=0, minute=0, second=0))
    time_table.append(dateAndTime)
    for i in range(143):
        dateAndTime += TEN_MINS
        time_table.append(dateAndTime)
    return time_table

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

def filter_signal(signal, threshold=1e8):
    fourier = fft(signal)
    frequencies = fftfreq(signal.size, d=20e-3/signal.size)
    fourier[frequencies > threshold] = 0
    return ifft(fourier)

TimeTable = Time_Table(inputdate)

filtered = filter_signal(np.asarray(l01), threshold=1e3)

plt.plot(TimeTable, l01)
plt.plot(TimeTable, filtered)
plt.grid()
plt.show()
