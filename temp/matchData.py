import datetime as dt
from pathlib import Path

import numpy as np
import terminaltables

NLDN_events, TASD_events, camera_triggers, intf = np.empty([1]), np.empty([1]), np.empty([1]), np.empty([1])
NLDN_events = NLDN_events[1:]
TASD_events = TASD_events[1:]
camera_triggers = camera_triggers[1:]
intf = intf[1:]

comp_NLDN_2_TASD = [['TASD Triggers', 'NLDN Data', 'delta']]
comp_TASD_2_TASD = [['TASD Triggers', 'TASD Triggers', 'delta']]
comp_cam_2_TASD = [['Camera Times', 'TASD Triggers', 'delta']]

half_window_1 = dt.timedelta(milliseconds=100)
half_window_2 = dt.timedelta(milliseconds=10)
half_window_3 = dt.timedelta(seconds=6)

NLDN = Path(__file__).resolve().parent / 'data' / 'NLDN.csv'
TASD = Path(__file__).resolve().parent / 'data' / 'TASD.txt'
camera = Path(__file__).resolve().parent / 'data' / 'Camera.csv'
out = Path(__file__).resolve().parent / 'out'


with open(NLDN, 'r') as file:
    for line in file:
        
        if 'EventTime' not in line:
            event = dt.datetime.strptime(line.split(',')[0][1:27], '%Y-%m-%dT%H:%M:%S.%f')

            NLDN_events = np.append(NLDN_events, event)

with open(TASD, 'r') as file:
    for line in file:
        
        event = dt.datetime.strptime(line[0:22], '%y%m%d %H %M %S.%f')
        
        diff_array = abs(NLDN_events - event)
        
        for i, delta in enumerate(diff_array):
            if delta <= half_window_1:
                comp_NLDN_2_TASD.append([event.strftime('%Y-%m-%d %H:%M:%S.%f'), NLDN_events[i], delta])

        diff_array = abs(TASD_events - event)
        for i, delta in enumerate(diff_array):
            if delta <= half_window_2:
                comp_TASD_2_TASD.append([event.strftime('%Y-%m-%d %H:%M:%S.%f'), TASD_events[i], delta])

        TASD_events = np.append(TASD_events, event)
        
with open(camera, 'r') as file:
    for line in file:
        camera_event = dt.datetime.strptime(line.split(',')[0][1:23], '%Y%m%dH%H%M%S.%f')
        
        diff_array = abs(TASD_events - camera_event)
        for i, delta in enumerate(diff_array):
            if delta <= half_window_3:
                comp_cam_2_TASD.append([camera_event.strftime('%Y-%m-%d %H:%M:%S.%f'), TASD_events[i], delta])


print(f'Comparing NLDN to TASD within {half_window_1}')
comp_NLDN_2_TASD = terminaltables.AsciiTable(comp_NLDN_2_TASD)
print(comp_NLDN_2_TASD.table)

with open(out / 'comp_NLDN_2_TASD.txt', 'w') as file:
    file.write(f'Comparing NLDN to TASD within {half_window_1}\n')
    file.write(comp_NLDN_2_TASD.table)
    
print()
print(f'Comparing TASD to TASD within {half_window_2}')
comp_TASD_2_TASD = terminaltables.AsciiTable(comp_TASD_2_TASD)
print(comp_TASD_2_TASD.table)

with open(out / 'comp_TASD_2_TASD.txt', 'w') as file:
    file.write(f'Comparing TASD to TASD within {half_window_2}\n')
    file.write(comp_TASD_2_TASD.table)

print()
print(f'Comparing Cam to TASD within {half_window_3}')
comp_cam_2_TASD = terminaltables.AsciiTable(comp_cam_2_TASD)
print(comp_cam_2_TASD.table)

with open(out / 'comp_cam_2_TASD.txt', 'w') as file:
    file.write(f'Comparing TASD to TASD within {half_window_3}\n')
    file.write(comp_cam_2_TASD.table)