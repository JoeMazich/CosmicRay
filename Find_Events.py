import geopy as gp
import numpy as np
import math

from scipy.spatial.distance import cdist, euclidean

from taTools import *

def find_NLDN_places(date, early_time, late_time):

    lat_long_array = np.empty((1,2))
    lat_long_array = np.delete(lat_long_array, 0, 0)
    lightning_filename = "DataDates/" + str(date) + "/NLDN.txt"
    file = open(lightning_filename,'r')

    for line in file:
        columns = line.split()

        temp = columns[1].split(":")
        hours = int(temp[0])
        minutes = int(temp[1])
        seconds = float(temp[2])
        time = hours*10000 + minutes*100 + seconds

        if(time >= early_time and time <= late_time):
            temp_x_y = np.array([[float(columns[2]), float(columns[3])]])
            lat_long_array = np.append(temp_x_y, lat_long_array, axis=0)

    file.close()

    return lat_long_array

def add_time(current, additional):
    hours_c = int(current / 10000)
    minutes_c = int(current / 100) - (hours_c * 100)
    seconds_c = current - (hours_c * 10000) - (minutes_c * 100)

    hours_a = int(additional / 10000)
    minutes_a = int(additional / 100) - (hours_a * 100)
    seconds_a = additional - (hours_a * 10000) - (minutes_a * 100)

    seconds = seconds_c + seconds_a
    minutes = minutes_c + minutes_a
    hours = hours_c + hours_a

    if (seconds >= 60):
        minutes = minutes + int(seconds / 60)
        seconds = seconds % 60
    if (minutes >= 60):
        hours = hours + int(minutes / 60)
        minutes = minutes % 60

    time = hours * 10000 + minutes * 100 + seconds

    return time

#geometric_median function written by orlp and remains unchanged
#obtained from https://stackoverflow.com/questions/30299267/geometric-median-of-multidimensional-points
#code released under SO license terms and zlib license
def geometric_median(X, eps=1e-5):
    y = np.mean(X, 0)

    while True:
        D = cdist(X, [y])
        nonzeros = (D != 0)[:, 0]

        Dinv = 1 / D[nonzeros]
        Dinvs = np.sum(Dinv)
        W = Dinv / Dinvs
        T = np.sum(W * X[nonzeros], 0)

        num_zeros = len(X) - np.sum(nonzeros)
        if num_zeros == 0:
            y1 = T
        elif num_zeros == len(X):
            return y
        else:
            R = (T - y) * Dinvs
            r = np.linalg.norm(R)
            rinv = 0 if r == 0 else num_zeros/r
            y1 = max(0, 1-rinv)*T + min(1, rinv)*y

        if euclidean(y, y1) < eps:
            return y1

        y = y1

def Surrounding_Dets(TASD):
    TL = TASD - 99
    TM = TASD + 1
    TR = TASD + 101
    ML = TASD - 100
    MR = TASD + 100
    BL = TASD - 101
    BM = TASD - 1
    BR = TASD + 99

    return [TL, TM, TR, ML, TASD, MR, BL, BM, BR]

def Find_Rate(date, TASD, early_time, late_time):

    dector_filename = "DataDates/" + str(date) + "/L0L1.txt"

    found_early = False

    early_lv0_rate = None
    late_lv0_rate = None

    file = open(dector_filename,'r')
    for line in file:
        columns = line.split()

        if (int(columns[1]) == early_time and int(columns[2]) == TASD):
            early_lv0_rate = float(columns[3])
            found_early = True
            if (int(columns[5]) != 0):
                print("Warning, det " + str(TASD) + "early time for rate is don't use")
            if (int(columns[6]) != 0):
                print("Warning, det " + str(TASD) + "early time for rate is warn")

        if (found_early and int(columns[1]) == late_time and int(columns[2]) == TASD):
            late_lv0_rate = float(columns[3])
            if (int(columns[5]) != 0):
                print("Warning, det " + str(TASD) + "late time for rate is don't use")
            if (int(columns[6]) != 0):
                print("Warning, det " + str(TASD) + "late time for rate is warn")
            break;

    file.close()

    if (early_lv0_rate == None and late_lv0_rate == None):
        return None
    elif (early_lv0_rate == None):
        return (math.inf)
    elif (late_lv0_rate == None):
        return (-math.inf)

    return ((late_lv0_rate - early_lv0_rate) / early_lv0_rate * 100)

def main():

    NLDN_centers = [] #temp storage for the geometric medians, will be elimated as we will do this on a per 10 min area
    early_time = 0

    for i in range(144): #grab the data in 10 min slots

        lat_long = find_NLDN_places(150915, early_time, add_time(early_time, 1000)) #grab the data in 10 min slots
        print("From " + str(early_time) + " to " + str(add_time(early_time, 1000)))

        if (len(lat_long) == 0):
            lat_long = np.zeros((1,2))

        print(lat_long)
        print("Median:")
        print(geometric_median(lat_long))
        print()
        print()

        NLDN_centers.append(geometric_median(lat_long))
        #remember to iterate the early time by 10 mins
        early_time = add_time(early_time, 1000)

    print(Find_Rate(150915, 1423, 140000, 141000))

main()