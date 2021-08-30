#%%
import geopy as gp
import numpy as np
import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from dataclasses import dataclass

from pathlib import Path
from typing import Callable, NewType, Tuple

from detectors import Detectors

import time # TEMPPP

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
    position: Tuple[float, float]
    peak_current: float
    type: str
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

        # Check to see if the DataDate file exists
        #   if so, load it
        #
        #   if not, make the DataDate file
        #   split the raw into L0L1 and NLDN
        #   load it
        #   make rates
        #   save the new data

        # Load everything needed - assuming there will be rates already there
        if self._file.is_dir():
            L0L1_file = self._file / 'L0L1.txt'
            NLDN_file = self._file / 'NLDN.txt'
            self._load_bytes(L0L1_file, self._L0L1_parse)
            self._load_bytes(NLDN_file, self._NLDN_parse)
        # Split raw data, load the splitted data, make the rates, save the total data, delete the splitted data
        else:
            self._warn(1, f'{self._file}, making a new one')
            Path.mkdir(self._file)
            
            start = time.perf_counter()
            self.parseAllRaw()
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
    # WILL NOT SAVE FILES
    def parseAllRaw(self) -> None:
        wd = self._file.parents[1]
        raw_data_path = wd.joinpath('RawData')

        raw_L0L1_files = raw_data_path / 'L0L1'
        raw_NLDN = raw_data_path / 'NLDN' / 'Raw_NLDN.txt'

        # Check to see if the year is in the filename (2014 -> file should have a 14 in it)
        for raw_L0L1 in raw_L0L1_files.iterdir():
            if str(self.date.year)[-2:] in raw_L0L1.name:
                self._load_bytes(raw_L0L1, self._L0L1_parse, raw=True)
      
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

    def save(self, defSure=False) -> None:
        imSure = False
        if not defSure:
            imSure = (input('Are you sure? Previous files will be deleted and replaced with this sessions L0 and NLDN! (Y/n): ') == 'Y')
        if defSure or imSure:
            L0L1_file = self._file / 'L0L1.txt'
            NLDN_file = self._file / 'NLDN.txt'

            if L0L1_file.is_file():
                try:
                    L0L1_file.unlink()
                except OSError as e:
                    self._warn(0, f'Could not delete {L0L1_file}\n{e}')

            if NLDN_file.is_file():
                try:
                    NLDN_file.unlink()
                except OSError as e:
                    self._warn(0, f'Could not delete {NLDN_file}\n{e}')

            
            with open(L0L1_file, 'w') as file:
                for k, v in self.L0.items():
                    file.write(f'{k} {v}\n')

            with open(NLDN_file, 'w') as file:
                for v in self.NLDN:
                    file.write(f'{v}\n')


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
                newNLDN = NLDN(event_datetime, (float(lat), float(long)), float(peak_current), type.decode('utf-8'))
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
    day1 = DataDate('140928', Detectors())

    newKey1 = KeyLv0(dt.date(2002, 12, 31), '1234')
    newKey2 = KeyLv0(dt.date(2002, 12, 31), '1234')