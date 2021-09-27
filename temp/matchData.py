import datetime as dt
import math
from pathlib import Path

import geopy
import numpy as np
import terminaltables

from taTools import clf2ivanov, gps2cart

NLDN_events, TASD_events, camera_triggers = [], [], []

comp_NLDN_2_TASD_time = [['TASD Triggers', 'NLDN Data', 'delta']]
comp_TASD_2_TASD_time = [['TASD Triggers', 'TASD Triggers', 'delta']]
comp_NLDN_2_TASD_location = [['TASD Triggers', 'NLDN Data', 'delta']]
comp_TASD_2_TASD_location = [['TASD Triggers', 'TASD Triggers', 'delta']]
comp_cam_2_TASD = [['Camera Times', 'TASD Triggers', 'TASD location', 'delta']]

culled_NLDN_2_TASD = [['TASD time', 'TASD location', 'NLDN time', 'NLDN location', 'Time delta', 'Distance delta']]
culled_TASD_2_TASD = [['1st TASD time', '1st TASD location', '2nd TASD time', '2nd TASD location', 'Time delta', 'Distance delta']]

NLDN_2_TASD_2_Cam = [['TASD time', 'NLDN time', 'Camera time', \
        'Delta TASD and NLDN time (seconds)', 'Delta TASD and Camera time (seconds)', \
        'TASD location', 'NLDN location', 'Distance between TASD and NLDN (km)']]

half_window_1 = dt.timedelta(milliseconds=500) # milliseconds = 500
half_window_2 = dt.timedelta(milliseconds=1) # milliseconds = 1
half_window_3 = dt.timedelta(seconds=1) # seconds = 1
max_distance = 30

NLDN = Path(__file__).resolve().parent / 'data' / 'nldn_20210818.csv'
TASD = Path(__file__).resolve().parent / 'data' / 'SD210818.rtuple.txt'
camera = Path(__file__).resolve().parent / 'data' / '21Aug18-19_HSV_INTF-raw-times.csv'
out = Path(__file__).resolve().parent / 'out'


with open(NLDN, 'r') as file:
    for line in file:
        
        if 'EventTime' not in line and ',' in line:
            split = line.split(',')
            event_time = dt.datetime.strptime(split[0][1:27], '%Y-%m-%dT%H:%M:%S.%f')
            gps = geopy.point.Point(float(split[1]), float(split[2]), 0)
            x, y, z = gps2cart(gps)
            
            l, j = [x], [y]
            clf2ivanov(l, j)
            x = l[0]
            y = j[0]
            
            NLDN_events.append([event_time, (x, y)])

with open(TASD, 'r') as file:
    for line in file:        
        event = dt.datetime.strptime(line[0:22], '%y%m%d %H %M %S.%f')
        x, y = [float(line.split()[7])], [float(line.split()[8])]
    
        
        diff_array = abs(np.asarray([t[0] for t in NLDN_events]) - event)
        
        for i, delta in enumerate(diff_array):
            if delta <= half_window_1:
                distance = math.sqrt((NLDN_events[i][1][0] - x[0]) ** 2 + (NLDN_events[i][1][1] - y[0]) ** 2)
                comp_NLDN_2_TASD_time.append([event.strftime('%Y-%m-%d %H:%M:%S.%f'), NLDN_events[i][0], delta])
                comp_NLDN_2_TASD_location.append([(x, y), NLDN_events[i][1], distance])
                
                if distance < max_distance:
                    culled_NLDN_2_TASD.append([event.strftime('%Y-%m-%d %H:%M:%S.%f'), (x, y), NLDN_events[i][0], \
                        NLDN_events[i][1], delta, distance])
                    
                    NLDN_2_TASD_2_Cam.append([event.strftime('%H:%M:%S.%f'), NLDN_events[i][0].strftime('%H:%M:%S.%f'), \
                        '', delta.total_seconds(), '', \
                        (float("{:.2f}".format(x[0])), (float("{:.2f}".format(y[0])))), \
                        (float("{:.2f}".format(NLDN_events[i][1][0])), \
                        float("{:.2f}".format(NLDN_events[i][1][1]))), \
                        "{:.2f}".format(distance)])

        diff_array = abs(np.asarray([t[0] for t in TASD_events]) - event)
        for i, delta in enumerate(diff_array):
            if delta <= half_window_2:
                distance = math.sqrt((TASD_events[i][1][0] - x[0]) ** 2 + (TASD_events[i][1][1] - y[0]) ** 2)
                comp_TASD_2_TASD_time.append([event.strftime('%Y-%m-%d %H:%M:%S.%f'), TASD_events[i][0], delta])
                comp_TASD_2_TASD_location.append([(x, y), TASD_events[i][1], distance])
                
                if distance < max_distance:
                    culled_TASD_2_TASD.append([event.strftime('%Y-%m-%d %H:%M:%S.%f'), (x, y), TASD_events[i][0], TASD_events[i][1], delta, distance])

        TASD_events.append([event, (x[0], y[0])])
        
with open(camera, 'r') as file:
    for line in file:
        if 'Flash' not in line:
            split = line.split(',')
            
            camera_event = dt.datetime.strptime(split[0][1:23], '%Y%m%dH%H%M%S.%f')
            
            diff_array = abs(np.asarray([t[0] for t in TASD_events]) - camera_event)
            for i, delta in enumerate(diff_array):
                if delta <= half_window_3:
                    comp_cam_2_TASD.append([camera_event.strftime('%Y-%m-%d %H:%M:%S.%f'), TASD_events[i][0], TASD_events[i][1], delta])

                    for data_point in NLDN_2_TASD_2_Cam:
                        if TASD_events[i][0].strftime('%H:%M:%S.%f') in data_point:
                            data_point[2] = camera_event.strftime('%H:%M:%S.%f')
                            data_point[4] = delta.total_seconds()

print(f'Comparing NLDN to TASD within {half_window_1}')
comp_NLDN_2_TASD_time = terminaltables.AsciiTable(comp_NLDN_2_TASD_time)
print(comp_NLDN_2_TASD_time.table)

with open(out / 'comp_NLDN_2_TASD_time.txt', 'w') as file:
    file.write(f'Comparing NLDN to TASD within {half_window_1}\n')
    file.write(comp_NLDN_2_TASD_time.table)
    
print()
print(f'Comparing TASD to TASD within {half_window_2}')
comp_TASD_2_TASD_time = terminaltables.AsciiTable(comp_TASD_2_TASD_time)
print(comp_TASD_2_TASD_time.table)

with open(out / 'comp_TASD_2_TASD_time.txt', 'w') as file:
    file.write(f'Comparing TASD to TASD within {half_window_2}\n')
    file.write(comp_TASD_2_TASD_time.table)

print()
print(f'Comparing Cam to TASD within {half_window_3}')
comp_cam_2_TASD = terminaltables.AsciiTable(comp_cam_2_TASD)
print(comp_cam_2_TASD.table)

with open(out / 'comp_cam_2_TASD.txt', 'w') as file:
    file.write(f'Comparing Cam to TASD within {half_window_3}\n')
    file.write(comp_cam_2_TASD.table)
    
    
print(f'Comparing NLDN to TASD within {half_window_1}')
comp_NLDN_2_TASD_location = terminaltables.AsciiTable(comp_NLDN_2_TASD_location)
print(comp_NLDN_2_TASD_location.table)

with open(out / 'comp_NLDN_2_TASD_location.txt', 'w') as file:
    file.write(f'Comparing NLDN to TASD within {half_window_1}\n')
    file.write(comp_NLDN_2_TASD_location.table)

print(f'Comparing TASD to TASD within {half_window_2}')
comp_TASD_2_TASD_location = terminaltables.AsciiTable(comp_TASD_2_TASD_location)
print(comp_TASD_2_TASD_location.table)

with open(out / 'comp_TASD_2_TASD_location.txt', 'w') as file:
    file.write(f'Comparing TASD to TASD within {half_window_2}\n')
    file.write(comp_TASD_2_TASD_location.table)



culled_TASD_2_TASD = terminaltables.AsciiTable(culled_TASD_2_TASD)
print(culled_TASD_2_TASD.table)

with open(out / 'culled_TASD_2_TASD.txt', 'w') as file:
    file.write(f'Comparing TASD to TASD within {half_window_2} and {max_distance}km\n')
    file.write(culled_TASD_2_TASD.table)


culled_NLDN_2_TASD = terminaltables.AsciiTable(culled_NLDN_2_TASD)
print(culled_NLDN_2_TASD.table)

with open(out / 'culled_NLDN_2_TASD.txt', 'w') as file:
    file.write(f'Comparing NLDN to TASD within {half_window_1} and {max_distance}km\n')
    file.write(culled_NLDN_2_TASD.table)

NLDN_2_TASD_2_Cam = terminaltables.AsciiTable(NLDN_2_TASD_2_Cam)
print(NLDN_2_TASD_2_Cam.table)

with open(out / 'NLDN_2_TASD_2_Cam.txt', 'w') as file:
    file.write(f'2021-09-12\n')
    file.write(f'Comparing NLDN to TASD within {half_window_1.total_seconds()} seconds\n')
    file.write(f'Comparing TASD to Camera within {half_window_3.total_seconds()} seconds\n')
    file.write(NLDN_2_TASD_2_Cam.table)
