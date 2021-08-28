#%%
import geopy as gp
import numpy as np
import datetime as dt
import pickle

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from dataclasses import dataclass

from pathlib import Path
from typing import Callable, NewType, Tuple

from detectors import Detectors

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

TAKE_OUT_DONTUSE = True
TAKE_OUT_WARN = True

@dataclass(frozen=True) # key object used to get Lv0 data
class KeyLv0:
    event_time: dt.datetime
    det_num: str

@dataclass # value object to hold the helpful Lv0 data
class ValLv0:
    lv0: float
    position: Tuple[float, float]
    tempature: float
    rate: float = None

@dataclass
class NLDN:
    event_datetime: dt.datetime
    position: Tuple[float, float]
    peak_current: float
    type: str
#%%

class DataDate:
    def __init__(self, date: str, detectors: Detectors) -> None:
        self.counter = 0

        self.date = dt.datetime.strptime(date, '%y%m%d')
        self.L0 = {}
        self.NLDN = []

        parent_dir = Path(__file__).resolve().parents[1]
        self._file = parent_dir.joinpath(f'DataDates/{date}')
        self._detectors = detectors

        self.__temp_storage = []

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
            self._load(L0L1_file, self._L0L1_parse)
            self._load(NLDN_file, self._NLDN_parse)
        # Split raw data, load the splitted data, make the rates, save the total data, delete the splitted data
        else:
            self._warn(1, f'{self._file}, making a new one')
            #Path.mkdir(self._file)
            
            start = time.perf_counter()
            self.makeTempDataFiles()
            stop = time.perf_counter()
            print(stop - start)

            self.findRates()
            self.deleteTempDataFiles()


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


    def makeTempDataFiles(self) -> None:
        wd = self._file.parents[1]
        raw_data_path = wd.joinpath('RawData')
        raw_L0L1_files = raw_data_path / 'L0L1'

        # Check to see if the year is in the filename (2014 -> file should have a 14 in it)
        for raw_L0L1 in raw_L0L1_files.iterdir():
            if str(self.date.year)[-2:] in raw_L0L1.name:
                self._raw_load(raw_L0L1, self._raw_L0L1_parse)
        
        # Now L0L1 is loaded into the temp storage
        with open('_temp_storage', 'wb') as file:
            pickle.dump(self.__temp_storage, file)


        raw_NLDN = raw_data_path / 'NLDN' / 'Raw_NLDN.txt'
        self._load(raw_NLDN, self._raw_NLDN_parse)

    def deleteTempDataFiles(self) -> None:
        pass
    
    def findRates(self) -> None:
        pass


    # Simple loading
    def _load(self, path: Path, parser: Callable[[str], None]) -> None:
        with open(path, 'rb') as file: 
            [parser(line) for line in file.readlines()]

    # Parsing for L0L1
    def _L0L1_parse(self, line: str) -> None:
        data = line.split()
        event_date, event_time, det_num, lv0, lv1, dontuse, warning, quality, temp = data[:9]

        if not TAKE_OUT_DONTUSE or dontuse == '0':
            if not TAKE_OUT_WARN or warning == '0':

                event_datetime = dt.datetime.strptime(event_date + event_time, '%y%m%d%H%M%S')

                newKey = KeyLv0(event_datetime, det_num)
                newVal = ValLv0(float(lv0), self._detectors.getCart(det_num), float(temp))

                # Check to see if rate has already been calculated
                if len(data) == 10:
                    newVal.rate = float(data[9])
                
                self.L0[newKey] = newVal
    
    def _NLDN_parse(self, line: str) -> None:
        event_date, event_time, lat, long, peak_current, type = line.split()
        event_datetime = dt.datetime.strptime(event_date + event_time[:14], '%Y-%m-%d%H:%M:%S.%f')
        newNLDN = NLDN(event_datetime, (float(lat), float(long)), float(peak_current), type)
        self.NLDN.append(newNLDN)

    # Loading for raw data
    def _raw_load(self, path: Path, parser: Callable[[str], None]) -> None:
        with open(path, 'rb') as file: 
            for line in file.readlines():
                if self.date.strftime('%y%m%d') in line:
                    self.__temp_storage.append(line)

    def _raw_L0L1_parse(self, line: str) -> None:
        if self.date.strftime('%y%m%d') in line:
            self.__temp_storage.append(line)
        
    def _raw_NLDN_parse(self, line: str) -> None:
        pass


    
    def _warn(self, id: int, comments: str = '') -> None:
        switcher = {
            0: 'Critical Error:',
            1: 'Could not find file:',
            2: 'Could not find data:',
        }
        print(switcher.get(id), comments)

#%%

if __name__ == '__main__':
    day = DataDate('140928', Detectors())
    newKey1 = KeyLv0(dt.date(2002, 12, 31), '1234')
    newKey2 = KeyLv0(dt.date(2002, 12, 31), '1234')