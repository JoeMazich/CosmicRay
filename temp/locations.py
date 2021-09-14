from taTools import *
import geopy
import numpy as np
import datetime as dt
from typing import Tuple, List
import math
import terminaltables

TASDevent1 = dt.datetime.strptime('2021-08-18 03:47:47.344377', '%Y-%m-%d %H:%M:%S.%f')
TASDevent2 = dt.datetime.strptime('2021-08-18 12:03:38.716317', '%Y-%m-%d %H:%M:%S.%f')
TASDevent3 = dt.datetime.strptime('2021-08-18 13:32:13.665480', '%Y-%m-%d %H:%M:%S.%f')
TASDevent4 = dt.datetime.strptime('2021-08-18 14:11:41.102353', '%Y-%m-%d %H:%M:%S.%f')

TASDevents = [TASDevent1, TASDevent2, TASDevent3, TASDevent4]

NLDNevent1 = dt.datetime.strptime('2021-08-18 03:47:47.331020', '%Y-%m-%d %H:%M:%S.%f')
NLDNevent2 = dt.datetime.strptime('2021-08-18 12:03:38.716544', '%Y-%m-%d %H:%M:%S.%f')
NLDNevent3 = dt.datetime.strptime('2021-08-18 13:32:13.665334', '%Y-%m-%d %H:%M:%S.%f')
NLDNevent4 = dt.datetime.strptime('2021-08-18 14:11:41.101943', '%Y-%m-%d %H:%M:%S.%f')

NLDNevents = [NLDNevent1, NLDNevent2, NLDNevent3, NLDNevent4]

TASD, NLDN = {}, {}

with open('TASDtriggers.txt', 'rb') as file:
    for line in file:
        event = dt.datetime.strptime(line[0:22].decode('utf-8'), '%y%m%d %H %M %S.%f')

        if event in TASDevents:
            TASD[event] = (float(line.split()[7]), float(line.split()[8]))


with open('NLDNdata.csv', 'rb') as file:
    for line in file:
        if b'EventTime' not in line:
            split = line.split(b',')
            event = dt.datetime.strptime(split[0][1:27].decode('utf-8'), '%Y-%m-%dT%H:%M:%S.%f')

            if event in NLDNevents:
                NLDN[event] = (float(split[1]), float(split[2]))


print('\nRaw TASD Trigger values')
for k, v in TASD.items():
    print(k, v)
print()

print('Raw NLDN values')
for k, v in NLDN.items():
    print(k, v)
print('\n.............................................\n')

def ivanov2clf(data: List[Tuple]) -> List[Tuple]:
    clf_coors = []
    for ivanov_coors in data:
        clf_coors.append( ((ivanov_coors[0]-12.2435)*1.200, (ivanov_coors[1]-16.4406)*1.200) )

    return clf_coors

def clf2ivanov(data: List[Tuple]) -> List[Tuple]:
    ivanov_coors = []
    for clf_coors in data:
        ivanov_coors.append( ( (clf_coors[0]/1.200+12.2435), (clf_coors[1]/1.200+16.4406) ) )

    return ivanov_coors

TASD_clf_coors = ivanov2clf(TASD.values())

for index, event in enumerate(TASD.keys()):
    TASD[event] = f'ivanov:{TASD[event]}, clf:{TASD_clf_coors[index]}'

print('TASD Trigger values')
for k, v in TASD.items():
    print(k, '/', v)
print()

list = []
for key, val in NLDN.items():
    gps = geopy.point.Point(val[0], val[1], 0)
    x, y, z = gps2cart(gps)
    list.append((x,y))
    NLDN[key] = f'lat/long:{val}, clf:{x,y}'
ivanov_NLDN = clf2ivanov(list)

print('NLDN values')
for k, v in NLDN.items():
    print(k, '/', v)
print('\n.............................................\n')


nTASD_dict, nNLDN_dict = {}, {}

for k, v in TASD.items():
    nTASD_dict[k] = v.split('clf:')[1]

for k, v in NLDN.items():
    nNLDN_dict[k] = v.split('clf:')[1]

print('Result TASD Trigger values')
for k, v in nTASD_dict.items():
    print(k, '/', v)
print()

print('Result NLDN values')
for k, v in nNLDN_dict.items():
    print(k, '/', v)
print()

def distance(coors1: str, coors2: str) -> float:
    coors1, coors2 = eval(coors1), eval(coors2)
    return math.sqrt((coors1[0] - coors2[0]) ** 2 + (coors1[1] - coors2[1]) ** 2)

distance1 = distance(nTASD_dict[TASDevent1], nNLDN_dict[NLDNevent1])
distance2 = distance(nTASD_dict[TASDevent2], nNLDN_dict[NLDNevent2])
distance3 = distance(nTASD_dict[TASDevent3], nNLDN_dict[NLDNevent3])
distance4 = distance(nTASD_dict[TASDevent4], nNLDN_dict[NLDNevent4])

data = [['TASD', 'NLDN', 'Distance(CLF coors)'], 
        [TASDevent1, NLDNevent1, distance1], 
        [TASDevent2, NLDNevent2, distance2],
        [TASDevent3, NLDNevent3, distance3], 
        [TASDevent4, NLDNevent4, distance4]]
table  = terminaltables.AsciiTable(data)
print(table.table)

for i, event in enumerate(NLDNevents):
    print(event, ivanov_NLDN[i])