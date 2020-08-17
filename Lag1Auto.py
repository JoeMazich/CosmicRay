from datetime import *
import numpy as np
import pandas as pd

TAKE_OUT_DONTUSE = True
TAKE_OUT_WARN = True
TEN_MINS = timedelta(minutes=10)

# change time that looks like 123456 to a datetime.time that looks like 12:34:56
def Time_P2D(plain_time):
    hour = int(plain_time[0:2])
    min = int(plain_time[2:4])
    sec = int(plain_time[4:6])
    return time(hour, min, sec)

# change time that looks like 12:34:56 to a datetime.time that looks like 12:34:56
# (ok yes it looks the same, but it is a datetime.time object, trust me)
def Time_C2D(colon_time):
    temp = colon_time.split(":")
    hour = int(temp[0])
    min = int(temp[1])
    temp2 = temp[2].split(".")
    sec = int(temp2[0])
    microsec = int(temp2[1][0:6])
    return time(hour, min, sec, microsec)

# change a date that looks like 180322 to a datetime.date that looks like 2018-03-22
def Date_P2D(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return date(year, month, day)

# change a date that looks like 180322 to a date that looks like 2018-03-22
def Date_P2D_num2(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return str(str(year) + "-" + str(month) + "-" + str(day))

# change a date like this: 2018-03-22 to a datetime.date
def Date_D2D(dashed_date):
    temp = dashed_date.split("-")
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    return date(year, month, day)

def Lv0(filename):
    time_det_lv0rate_CCoors = {}
    file = open("DataDates/" + filename + "/L0L1.txt", 'r')

    for line in file:
        columns = line.split()
        if not TAKE_OUT_DONTUSE or int(columns[5]) == 0:
            if not TAKE_OUT_WARN or int(columns[6]) == 0:
                time_det_lv0rate_CCoors[datetime.combine(Date_P2D(columns[0]), (Time_P2D(columns[1]))), columns[2]] = [float(columns[3]), [0,0]]

    file.close()

    return time_det_lv0rate_CCoors

def FindRates(dict):
    for time_det, lv0_latlong in dict.items():
        # get all necessary info
        this_lv0 = lv0_latlong[0]
        this_det = time_det[1]
        this_time = time_det[0]
        next_time = time_det[0] + TEN_MINS
        # check to see if the same det exsists ten mins after in the dict
        if (next_time, this_det) in dict.keys():
            # if it is, then find the rate of change and append it to the list (the value of the dict)
            # at this_time (not at next_time)
            # VV This VV exsists here because we had to check it exsisted first
            next_lv0 = dict[next_time, this_det][0]
            rate = ((next_lv0 - this_lv0) / this_lv0) * 100
            lv0_latlong.append(rate)

        else:
            #if not, append 0, 0 to this time as a place holder (one for rate the other for rate cutoff)
            lv0_latlong.extend([0, 0])



input_date = input("What date? ")
input_det = input("What det? ")
Lv0dict = Lv0(input_date)
FindRates(Lv0dict)

lv0ratesforauto = []

for key, value in Lv0dict.items():
    if key[1] == input_det:
        lv0ratesforauto.append(value[2])

sr = pd.Series(lv0ratesforauto)
index_ = pd.date_range(Date_P2D_num2(input_date) + ' 00:00', periods = len(lv0ratesforauto), freq ='H')
sr.index = index_
print(sr.autocorr())
