from detectors import Detectors
from dataDate import DataDate

from typing import List
                                                                                                         
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

class DataDates:
    def __init__(self) -> None:
        self._detectors = Detectors()
        self._datadates = {}

    def __getitem__(self, id: str) -> DataDate:
        return self._datadates[id]

    def newDataDate(self, date: str) -> None:
        newDate = DataDate(date, self._detectors)
        self._datadates[date] = newDate

    # faster for loading more than one date
    def load_dates(self, dates: List[str]) -> None:
        pass

    # make animation function to animate multiple dates in one fig??