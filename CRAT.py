import os
import re
import sys
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion.word_completer import WordCompleter
from prompt_toolkit.history import FileHistory

from src.dataDates import DataDates
from src.OneDimension import getDataForOneD, plotOneD, plotLv0vsTemp, plotHans
from src.Utils import stringToDatetime
from src.detectors import NearDets


class DataDatePrompt:
    
    def __init__(self) -> None:

        #self._check_raw_files()

        self._dates = DataDates()

        self._commands = {
            'help': self._help,
            'exit': '_',
            'clear': self._clear,
            'loadYear': self._dates.loadAndSaveYear,
            'loadDate': self._dates.newDataDate,
            'save': self._save,
            'oneD': self._oneD,
            'tempNormalize': self._temp_norm,
        }

        self._commands_help = {
            'exit': self._des_exit,
            'clear': self._des_clear,
            'loadYear': self._des_loadYear,
            'loadDate': self._des_loadDate,
            'save': self._des_save,
            'oneD': self._des_oneD,
        }

        command_completer = WordCompleter(self._commands.keys())

        while True:
            user_input = prompt(u'/> ',
                                history=FileHistory('history.txt'),
                                auto_suggest=AutoSuggestFromHistory(),
                                ).split()

            user_command, args = user_input[0], user_input[1:]

            try:
                if 'help' in args:
                    self._commands_help[user_command]()
                elif user_command == 'exit':
                    break
                elif user_command in self._commands:
                    self._commands[user_command](*args)
                else:
                    print('Not a command!')
            except TypeError as e:
                    print(e)

    def _des_exit(self) -> None:
        self._des('exit', 'Will exit the terminal', ['exit'])

    def _des_clear(self) -> None:
        self._des('clear', 'Will clear the screen', ['clear'])

    def _des_loadYear(self) -> None:
        self._des('loadYear', 'Will load a years worth of data into buffer based on any NLDN activity and save to files (NOT TO MOVIES)', ['loadYear 2015'], ['year'])

    def _des_loadDate(self) -> None:
        self._des('loadDate', 'Will load a specified day into buffer', ['loadDate 120121'], ['date'])

    def _des_save(self) -> None:
        self._des('save', 'Will save buffered dates into files or movies', ['save dates', 'save movies'], ['"dates" || "movies"'])
    
    def _des_oneD(self) -> None:
        self._des('oneD', 'Will create a one dimension level0 and temperature plot from a LOADED date', ['oneD 140927 1415 18:20:00 19:20:00', 'oneD 150515 1308 07:00:00 16:30:00 8:10:00'], ['date', 'detector number', 'starting time', 'ending time', '~marked time'])

    def _des(self, name: str, des: str, examples: List[str], func_inputs: List[str] = None) -> None:
        print(f'\n{name}\n')
        print(f'     {des}\n')

        if func_inputs:
            print('     Inputs: ', end='')
            for func_input in func_inputs:
                print(f'({func_input}) ', end='')
            print('\n')

        print(f'     Examples: {examples[0]}')
        for example in examples[1:]:
            print(f'               {example}')
        print()

    def _help(self) -> None:
        for help_command in self._commands_help:
            print('========================================================================================')
            self._commands_help[help_command]()
            print('========================================================================================')

    def _clear(self) -> None:
        if sys.platform == 'linux' or sys.platform == 'linux2' or sys.platform == 'darwin':
            os.system('clear')
        elif sys.platform == 'win32':
            os.system('cls')

    def _save(self, arg: str) -> None:

        valid_args = {
            'dates': self._dates.saveDates,
            'movies': self._dates.saveMovies
        }

        if arg not in valid_args.keys():
            print('\nNot a valid argument')

        else:
            valid_args[arg]()

    def _oneD(self, date: str, detector_number: str, start_time: str, end_time: str, marked_time: str = None) -> None:
        if date in self._dates.keys():
            one_d_data = getDataForOneD(self._dates[date], detector_number, stringToDatetime(start_time), stringToDatetime(end_time))
            plotOneD(*one_d_data, stringToDatetime(marked_time))
        else:
            print('Date not loaded!')

    def _hansPlots(self, date: str, center_detector: str, square_radius: int ) -> None:
        # TODO - dynamically choose y values to normalize plots in plotHans
        # TODO - add command
        start_time, end_time = '00:00:00', '23:50:00'

        near_detectors = NearDets(center_detector, square_radius * 2 + 1, True)
        plotHans(self._dates[date], near_detectors, square_radius * 2 + 1, stringToDatetime(start_time), stringToDatetime(end_time))

    def _temp_norm(self, date: str) -> None:

        total_level0, total_tempature = [], []
        start_time, end_time = '23:40:00', '23:50:00'

        for detector_number in self._dates.detectors.getAllDets():
            _, level0, tempature, _ = getDataForOneD(self._dates[date], detector_number, stringToDatetime(start_time), stringToDatetime(end_time))
            total_level0.append(level0)
            total_tempature.append(tempature)

        plotLv0vsTemp(total_level0, total_tempature)

        '''
        for date in self._dates.keys():
            for detector_number in self._dates.detectors.getAllDets():
                _, level0, tempature, _ = getDataForOneD(self._dates[date], detector_number, stringToDatetime(start_time), stringToDatetime(end_time))

                per_detector_level0 += level0
                per_detector_tempature += tempature

            total_level0.append(per_detector_level0)
            total_tempature.append(per_detector_tempature)
            per_detector_level0, per_detector_tempature = [], []

        plotLv0vsTemp(total_level0, total_tempature)'''

    def _check_raw_files(self) -> None:

        assert os.path.exists('./RawData') == True
        assert os.path.exists('./RawData/NLDN') == True
        assert os.path.exists('./RawData/L0L1') == True
        assert os.path.exists('./RawData/NLDN/Raw_NLDN.txt') == True
        year = re.compile('./RawData/L0L1/l0_10min_\d\d.txt')
        #assert os.path.exists('') == True


if __name__ == '__main__':

    try:
        DataDatePrompt()
    except KeyboardInterrupt:
        print('\nTerminal interupted')
