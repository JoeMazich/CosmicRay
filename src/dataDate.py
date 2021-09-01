#%%
import geopy as gp
import numpy as np
import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from dataclasses import dataclass

from pathlib import Path
from typing import Callable, Tuple

from detectors import Detectors
from taTools import *

import time

#%%
                                                                                                         
#                                                                                                         
#     ,---,                   ___                    ,---,                   ___                           
#   .'  .' `\               ,--.'|_                .'  .' `\               ,--.'|_                         
# ,---.'     \              |  | :,'             ,---.'     \              |  | :,'                        
# |   |  .`\  |             :  : ' :             |   |  .`\  |             :  : ' :                
# :   : |  '  |  ,--.--.  .;__,'  /    ,--.--.   :   : |  '  |  ,--.--.  .;__,'  /     ,---.     
# |   ' '  ;  : /       \ |  |   |    /       \  |   ' '  ;  : /       \ |  |   |     /     \  
# '   | ;  .  |.--.  .-. |:__,'| :   .--.  .-. | '   | ;  .  |.--.  .-. |:__,'| :    /    /  |   
# |   | :  |  ' \__\/: . .  '  : |__  \__\/: . . |   | :  |  ' \__\/: . .  '  : |__ .    ' / | 
# '   : | /  ;  ," .--.; |  |  | '.'| ," .--.; | '   : | /  ;  ," .--.; |  |  | '.'|'   ;   /|
# |   | '` ,/  /  /  ,.  |  ;  :    ;/  /  ,.  | |   | '` ,/  /  /  ,.  |  ;  :    ;'   |  / |
# ;   :  .'   ;  :   .'   \ |  ,   /;  :   .'   \;   :  .'   ;  :   .'   \ |  ,   / |   :    |
# |   ,.'     |  ,     .-./  ---`-' |  ,     .-./|   ,.'     |  ,     .-./  ---`-'   \   \  /   
# '---'        `--`---'              `--`---'    '---'        `--`---'                `----'               
#                                                                                   *with python 3.8
#
#

# self._detectors.getCart(det_num)

TAKE_OUT_DONTUSE = True
TAKE_OUT_WARN = True
ACTIVE_WARNINGS = True

TEN_MINS = dt.timedelta(minutes=10)

CMAP_COLORS_TASD = ['purple', 'blue', 'cyan', 'green', 'orange', 'red', 'maroon'] # set the colors for the 2D map
CMAP_BOUNDS_TASD = [-5, -3, -1, -0.5, 0.5, 1, 3, 5] # set the bounds for the colors on the 2D map [-5, -3, -1, -0.5, 0.5, 1, 3, 5]

CMAP_COLORS_TEMP = ['#fc00b6', '#8e0da8', '#0021ff', 'cyan', 'green', 'orange', 'red', '#b60909', '#530028']
CMAP_BOUNDS_TEMP = [-30, -5, -3, -1, -0.5, 0.5, 1, 3, 5, 30] # set the bounds for the colors on the 2D map / default is [-30, -5, -3, -1, -0.5, 0.5, 1, 3, 5, 30]

ANI_SPEED = 900

TIME_NLDN_IS_ON = dt.timedelta(minutes=20)

@dataclass(frozen=True) # key object used to get Lv0 data
class KeyLv0:
    event_datetime: dt.datetime
    det_num: str
    def __str__(self) -> str:
        edt = self.event_datetime.strftime('%y%m%d %H%M%S')
        return f'{edt} {self.det_num}'

@dataclass # value object to hold the helpful Lv0 data
class ValLv0:
    lv0: float
    lv1: float
    dontuse: int
    warning: int
    quality: int
    tempature: float
    rate: float = None
    def __str__(self) -> str:
        return f'{self.lv0} {self.lv1} {self.dontuse} {self.warning} {self.quality} {self.tempature} {self.rate}'

@dataclass
class NLDN:
    event_datetime: dt.datetime
    ll_position: Tuple[float, float]
    peak_current: float
    type: str
    cc_position: Tuple[float, float]
    def __str__(self) -> str:
        edt = self.event_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
        return f'{edt} {self.position[0]} {self.position[1]} {self.peak_current} {self.type}'
#%%

class DataDate:
    def __init__(self, date: str, detectors: Detectors) -> None:

        self.date = dt.datetime.strptime(date, '%y%m%d')
        self.L0 = {}
        self.NLDN = []

        parent_dir = Path(__file__).resolve().parents[1]
        self._file = parent_dir.joinpath(f'DataDates/{date}')
        self._detectors = detectors

        self.__warnings = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

        # Load everything needed - assuming there will be rates already there
        if self._file.is_dir():
            L0L1_file = self._file / 'L0L1.txt'
            NLDN_file = self._file / 'NLDN.txt'

            start = time.perf_counter()
            self._load_bytes(L0L1_file, self._L0L1_parse)
            stop = time.perf_counter()
            load_L0L1_timing = (stop - start)

            start = time.perf_counter()
            self._load_bytes(NLDN_file, self._NLDN_parse)
            stop = time.perf_counter()
            load_NLDN_timing = (stop - start)

            print(f'Loading L0L1 took: {load_L0L1_timing} seconds\nLoading NLDN took: {load_NLDN_timing} seconds')

            
        # Split raw data, load the splitted data, make the rates, save the total data, delete the splitted data
        else:
            self._warn(1, f'{self._file}, making a new one')
            Path.mkdir(self._file)
            
            start = time.perf_counter()
            self.parseAndLoadFromRaw()
            stop = time.perf_counter()
            parseAllRaw_timing = (stop - start)

            start = time.perf_counter()
            self.findRates()
            stop = time.perf_counter()
            findRates_timing = (stop - start)

            start = time.perf_counter()
            self.save(defSure=True)
            stop = time.perf_counter()
            save_timing = (stop - start)

            print(f'Parsing from raw data took: {parseAllRaw_timing} seconds\nFinding the Rates took: {findRates_timing} seconds\nSaving took: {save_timing} seconds')

    def __str__(self) -> str:
        return self.date.strftime('%Y-%m-%d')

    def __len__(self) -> int:
        # Number of points we have in the dataset for the day
        return len(self.L0)

    def __getitem__(self, id: KeyLv0) -> float:
        # Retrieve a data based on time and detector
        try:
            return self.L0[id]

        except KeyError:
            time = id[0].strftime('%Y-%m-%d %H:%M:%S')
            detector = id[1]
            date = self.date.strftime('%Y-%m-%d')

            self._warn(2, (f'({time = }, {detector = }) key in {date} data'))
            return None


    # Cut through the large data files over time and save relevant data in self.L0 and self.NLDN
    # WILL NOT SAVE FILES, WILL ERASE CURRENT self.L0 and self.NLDN
    def parseAndLoadFromRaw(self, parseTASD = True, parseNLDN = True) -> None:
        wd = self._file.parents[1]
        raw_data_path = wd.joinpath('RawData')

        raw_L0L1_files = raw_data_path / 'L0L1'
        raw_NLDN = raw_data_path / 'NLDN' / 'Raw_NLDN.txt'

        # Check to see if the year is in the filename (2014 -> file should have a 14 in it)
        if (parseTASD):
            self.L0.clear()
            for raw_L0L1 in raw_L0L1_files.iterdir():
                if str(self.date.year)[-2:] in raw_L0L1.name:
                    self._load_bytes(raw_L0L1, self._L0L1_parse, raw=True)

        if (parseNLDN):
            self.NLDN.clear()
            self._load_bytes(raw_NLDN, self._NLDN_parse, raw=True)
    
    def findRates(self) -> None:
        
        for this_key, this in self.L0.items():
            previous_key = KeyLv0(this_key.event_datetime - TEN_MINS, this_key.det_num)
            try:
                if previous_key in self.L0.keys():
                    previous = self.L0[previous_key]

                    this.rate = ((this.lv0 - previous.lv0) / previous.lv0) * 100
                else:
                    self._warn(5, f'{this_key}')
            except Exception as e:
                self._warn(4, f'{this_key}\n{e}\n')

    def save(self, defSure = False, saveL0L1 = True, saveNLDN = True) -> None:

        imSure = False

        if not defSure:
            imSure = input('Are you sure? Previous files will be deleted and replaced with this sessions L0 and NLDN! (Y/n): ')

            valid_input = ['y', 'Y', 'n', 'N']
            while (imSure not in valid_input):
                imSure = input('Invalid input (Y/n):')

            imSure = (imSure == 'Y' or imSure == 'y')

        if defSure or imSure:
            L0L1_file = self._file / 'L0L1.txt'
            NLDN_file = self._file / 'NLDN.txt'

            if (saveL0L1):
                if L0L1_file.is_file():
                    try:
                        L0L1_file.unlink()
                    except OSError as e:
                        self._warn(0, f'Could not delete {L0L1_file}\n{e}')

                with open(L0L1_file, 'w') as file:
                    for k, v in self.L0.items():
                        file.write(f'{k} {v}\n')

            if (saveNLDN):
                if NLDN_file.is_file():
                    try:
                        NLDN_file.unlink()
                    except OSError as e:
                        self._warn(0, f'Could not delete {NLDN_file}\n{e}')

                with open(NLDN_file, 'w') as file:
                    for v in self.NLDN:
                        file.write(f'{v}\n')

    # Make this more dynamic - choose what goes where for example
    def animate(self) -> None:
        
        

        def update(frame: int) -> None:
            this_time = self.date + TEN_MINS * frame

            offsets1, offsets2, colors = [], [], []

            for key, value in self.L0.items():
                if key.event_datetime == this_time and value.rate:
                    offsets1.append(self._detectors.getCart(key.det_num))
                    colors.append(value.rate)
            sd_sensors_readings.set_offsets(offsets1 if offsets1 else [(None, None)])
            sd_sensors_readings.set_array(np.asarray(colors))

            offsets1.clear()
            colors.clear()

            for value in self.NLDN:
                if value.event_datetime <= (this_time + TEN_MINS) and  value.event_datetime >= (this_time + TEN_MINS - TIME_NLDN_IS_ON):
                    if value.type == 'C':
                        offsets1.append(value.cc_position)
                    elif value.type == 'G':
                        offsets2.append(value.cc_position)
            NLDN_C_lightning_readings.set_offsets(offsets1 if offsets1 else [(None, None)])
            NLDN_G_lightning_readings.set_offsets(offsets2 if offsets2 else [(None, None)])
            

            return list_plots

        fig = plt.figure()

        cmap_TASD = mpl.colors.ListedColormap(CMAP_COLORS_TASD)
        norm_TASD = mpl.colors.BoundaryNorm(CMAP_BOUNDS_TASD, cmap_TASD.N)

        cmap_Temp = mpl.colors.ListedColormap(CMAP_COLORS_TEMP)
        norm_Temp = mpl.colors.BoundaryNorm(CMAP_BOUNDS_TEMP, cmap_Temp.N)

        gs = fig.add_gridspec(2, 2)

        TASD_ax = fig.add_subplot(gs[0,0])
        TASD_ax.title.set_text("Rate Change")
        TASD_ax.set_xlim(-25, 25)
        TASD_ax.set_ylim(-28, 23)
        sd_sensors = TASD_ax.scatter(self._detectors.tasdx, self._detectors.tasdy, c='yellow', s=7, marker='.')
        sd_sensors_readings = TASD_ax.scatter([], [], c=[], s=7, cmap=cmap_TASD, norm=norm_TASD, marker='s')
        NLDN_G_lightning_readings = TASD_ax.scatter([], [], c='.4', s=10, marker='+')
        NLDN_C_lightning_readings = TASD_ax.scatter([], [], c='black', s=10, marker='+')
        plt.colorbar(sd_sensors_readings)
        
        list_plots = [sd_sensors_readings, NLDN_C_lightning_readings, NLDN_G_lightning_readings]

        anim = animation.FuncAnimation(fig, update, interval=ANI_SPEED, blit=True, repeat=True, frames=144)

        plt.show()

    # Simple loading, parser should return True if/when it can tell it is done
    def _load_bytes(self, path: Path, parser: Callable[[str], None], raw: bool = False) -> None:
        with open(path, 'rb') as file:
            for line in file.readlines():
                if parser(line, raw):
                    break

    def _L0L1_parse(self, line: str, raw: bool) -> bool:
        try:
            data = line.split()
            event_date, event_time, det_num, lv0, lv1, dontuse, warning, quality, temp = data[:9]
            event_datetime = dt.datetime.strptime((event_date + event_time).decode('utf-8'), '%y%m%d%H%M%S')
            # If parsing from raw data lines, we find a date that matches
            if raw and (self.date.date() == event_datetime.date()):
                # add it to the L0 dict
                newKey = KeyLv0(event_datetime, det_num.decode('utf-8'))
                newVal = ValLv0(float(lv0), float(lv1), int(dontuse), int(warning), int(quality), float(temp))
                self.L0[newKey] = newVal
                return False

                # Issue with this simple speed up - data errors can make some dates look like true dates later - 2052 date was found in 2014 file
                '''# If parsing from raw data lines, and we find a date that occurse after ours
                elif raw and self.date.date() < event_datetime.date():
                    print(self.date.date(), event_datetime.date())
                    # We are done because the data is ordered
                    return True'''

            # If not raw data, we know we got the rate, etc.
            elif not raw and (not TAKE_OUT_DONTUSE or dontuse == b'0') and (not TAKE_OUT_WARN or warning == b'0'):

                rate = (float(data[9]) if data[9] != b'None' else None)

                event_datetime = dt.datetime.strptime((event_date + event_time).decode('utf-8'), '%y%m%d%H%M%S')
                newKey = KeyLv0(event_datetime, det_num.decode('utf-8'))
                newVal = ValLv0(float(lv0), float(lv1), int(dontuse), int(warning), int(quality), float(temp), rate)
                self.L0[newKey] = newVal
                return False

        # If Exception is raised
        except Exception as e:
            self._warn(3, f'{line}\n{e}\n') # warn user

        # But assume that we are not done parsing
        return False
    
    def _NLDN_parse(self, line: str, raw: bool) -> bool:
        try:
            event_date, event_time, lat, long, peak_current, type = line.split()
            event_datetime = dt.datetime.strptime((event_date + event_time[:14]).decode('utf-8'), '%Y-%m-%d%H:%M:%S.%f')

            # If line is raw and the date matches or if the line is not raw, load it into NLDN
            if (raw and (self.date.date() == event_datetime.date())) or not raw:

                gps = gp.point.Point(float(lat), float(long), 0)
                x, y, z = gps2cart(gps)

                newNLDN = NLDN(event_datetime, (float(lat), float(long)), float(peak_current), type.decode('utf-8'), (x, y))
                self.NLDN.append(newNLDN)
            
            # If line is raw and the date is past our date, we know we can stop
            elif raw and self.date.date() < event_datetime.date():
                return True

        except Exception as e:
            self._warn(3, f'{line}\n{e}\n')
        return False        
    

    def _warn(self, id: int, comments: str = '') -> None:
        switcher = {
            0: 'Critical Error: ',
            1: 'Could not find file: ',
            2: 'Could not find data: ',
            3: 'Parser failed parsing line: ',
            4: 'Could not make rate: ',
            5: 'Could not find previous lv0: ',
        }
        warning = switcher.get(id) + comments + '\n'
        self.__warnings[id].append(warning)

        if ACTIVE_WARNINGS or id == 0:
            print(warning)
    

#%%

if __name__ == '__main__':
    day1 = DataDate('140927', Detectors())

    day1.animate()

    newKey1 = KeyLv0(dt.date(2002, 12, 31), '1234')
    newKey2 = KeyLv0(dt.date(2002, 12, 31), '1234')