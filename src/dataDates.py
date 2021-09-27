import sys
from pathlib import Path
from typing import List

from alive_progress import alive_bar

from dataDate import ACTIVE_WARNINGS, DataDate
from detectors import Detectors

#                                                                                                         
#     ,---,                   ___                    ,---,                   ___                           
#   .'  .' `\               ,--.'|_                .'  .' `\               ,--.'|_                         
# ,---.'     \              |  | :,'             ,---.'     \              |  | :,'                        
# |   |  .`\  |             :  : ' :             |   |  .`\  |             :  : ' :             .--.--.    
# :   : |  '  |  ,--.--.  .;__,'  /    ,--.--.   :   : |  '  |  ,--.--.  .;__,'  /     ,---.   /  /    '   
# |   ' '  ;  : /       \ |  |   |    /       \  |   ' '  ;  : /       \ |  |   |     /     \ |  :  /`./   
# '   | ;  .  |.--.  .-. |:__,'| :   .--.  .-. | '   | ;  .  |.--.  .-. |:__,'| :    /    /  ||  :  ;_     
# |   | :  |  ' \__\/: . .  '  : |__  \__\/: . . |   | :  |  ' \__\/: . .  '  : |__ .    ' / | \  \    `.  
# '   : | /  ;  ," .--.; |  |  | '.'| ," .--.; | '   : | /  ;  ," .--.; |  |  | '.'|'   ;   /|  `----.   \ 
# |   | '` ,/  /  /  ,.  |  ;  :    ;/  /  ,.  | |   | '` ,/  /  /  ,.  |  ;  :    ;'   |  / | /  /`--'  / 
# ;   :  .'   ;  :   .'   \ |  ,   /;  :   .'   \;   :  .'   ;  :   .'   \ |  ,   / |   :    |'--'.     /  
# |   ,.'     |  ,     .-./  ---`-' |  ,     .-./|   ,.'     |  ,     .-./  ---`-'   \   \  /   `--'---'   
# '---'        `--`---'              `--`---'    '---'        `--`---'                `----'               
#                                                                                   *with python 3.8       
#

ACTIVE_WARNINGS = False

class DataDates:
    def __init__(self) -> None:
        
        self._detectors = Detectors()
        self._datadates = {}
        
        parent_dir = Path(__file__).resolve().parents[1]
        self.__RawData = parent_dir.joinpath('RawData')
        self.__raw_l0_filenames = []
        self.__warnings = {1: [], 2: []}

    def __getitem__(self, id: str) -> DataDate:
        return self._datadates[id]


    def newDataDate(self, date: str) -> None:
        newDate = DataDate(date, self._detectors)
        self._datadates[date] = newDate

    # Function that gets all interesting dates in a year
    def loadYear(self, year: str) -> None:
        interesting_dates = []
        
        NLDN_file = self.__RawData / 'NLDN/Raw_NLDN.txt'
        
        with open(NLDN_file, 'r') as file:
            for line in file.readlines():
                event_date = line.split()[0]
                event_date = f'{event_date[2:4]}{event_date[5:7]}{event_date[8:10]}'
                
                if (t := event_date) not in interesting_dates and (t[:2] == year[2:4]):
                    interesting_dates.append(t)
                
        self.loadDates(interesting_dates)

    # Faster for loading more than one date
    def loadDates(self, dates: List[str]) -> None:

        new_l0_filenames = []
        for date in dates:
            if date not in self._datadates:
                self._datadates[date] = DataDate(date, self._detectors, man_load=True)

                if (l0_filename := f'l0_10min_{date[:2]}.txt') not in new_l0_filenames:
                    new_l0_filenames.append(l0_filename)
                    self.__raw_l0_filenames.append(l0_filename)

        for l0_filename in new_l0_filenames:
            path = self.__RawData.joinpath(f'L0L1/{l0_filename}')
            
            with open(path, 'rb') as file:
                file_lines = file.readlines()
                file_length = len(file_lines)

                with alive_bar(file_length, title=path.name, monitor=False, bar='classic', spinner='twirl') as bar:
                    for line in file_lines:
                        
                        try:                            
                            if (event_date := line.split()[0].decode('utf-8')) in dates:
                                self._datadates[event_date].L0L1_parse(line, raw=True)
                        except Exception as e:
                            self._warn(2, f'{line}\n{e}')
                        bar()
                        
        path = self.__RawData.joinpath(f'NLDN/Raw_NLDN.txt')
        
        with open(path, 'rb') as file:
            file_lines = file.readlines()
            file_length = len(file_lines)

            with alive_bar(file_length, title=path.name, monitor=False, bar='classic', spinner='twirl') as bar:
                for line in file_lines:
                    try:
                        dline = line[:10].decode('utf-8')
                        if (event_date := f'{dline[2:4]}{dline[5:7]}{dline[8:10]}') in dates:
                            self._datadates[event_date].NLDN_parse(line, raw=True)
                    except Exception as e:
                        self._warn(2, f'{line}\n{e}')
                    bar()

    def saveDates(self) -> None:
        for dataDate in self._datadates.values():
            dataDate.save(defSure=True)

    def _warn(self, id: int, comments: str = '') -> None:
        switcher = {
            1: 'Critical Warning: ',
            2: 'Parser could not parse date: ',
        }
        warning = switcher.get(id) + comments + '\n'
        self.__warnings[id].append(warning)

        if ACTIVE_WARNINGS or id == 1:
            print(warning)
    
if __name__ == '__main__':
    dates = DataDates()
    dates.loadYear('2014')
    
    dates.saveDates()
    
    for k, v in dates._datadates.items():
        print(k, v)
