import math
import sys
from pathlib import Path
from typing import List, Tuple

root_file = r'{}'.format(Path(__file__).resolve().parents[1])
sys.path.append(root_file)

import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
from dataDate import DataDate, KeyLv0
from detectors import Detectors

TIME_GRANULARITY = dt.timedelta(minutes=10)

# Get the oneD plot with regard to the self-explainoroty parameters (times are inclusive on both sides)
def getDataForOneD(dataDate: DataDate, detector_number: str, start_time: dt.time, end_time: dt.time):

    looking_time = start_time
    times_x, level0_y, tempature_y, level0_errors = [], [], [], []

    while looking_time <= end_time:
        event_datetime = dt.datetime.combine(dataDate.date.date(), looking_time.time())
        key = KeyLv0(event_datetime, detector_number)
        level0 = dataDate[key].lv0
        times_x.append(key.event_datetime)
        level0_y.append(level0)
        tempature_y.append(dataDate[key].tempature)

        error = ( 1 / math.sqrt( level0 * 60 * 10 ) ) * level0
        level0_errors.append(error)

        looking_time += TIME_GRANULARITY

    return (times_x, level0_y, tempature_y, level0_errors)

def plotOneD(times_x: List[dt.datetime], level0_y: List[float], tempature_y: List[float], level0_errors: List[float], marked_time: dt.time = None) -> None:

    if not times_x:
        print('No times specified!')
        return

    fig = plt.figure(figsize=(6, 10))
    fig.suptitle(times_x[0].date(), fontsize=20)
    gs = fig.add_gridspec(2, 1, left=0.12, right=0.93, top=0.93, bottom=0.05, wspace=0.2, hspace=0.07)

    Lv0ax = fig.add_subplot(gs[0, 0])
    Lv0ax.errorbar(times_x, level0_y, yerr=level0_errors, capsize=2, elinewidth=1)

    Tempax = fig.add_subplot(gs[1, 0])
    Tempax.plot(times_x, tempature_y)

    if marked_time:
        marked_datetime = dt.datetime.combine(times_x[0].date(), marked_time.time())

        Lv0ax.plot([marked_datetime, marked_datetime], [0, 1000])
        Lv0ax.set_ylim([min(level0_y) - 3, max(level0_y) + 3])

        Tempax.plot([marked_datetime, marked_datetime], [0, 1000])
        Tempax.set_ylim([min(tempature_y) - 3, max(tempature_y) + 3])

    # Plot parameters to look nicer
    Tempax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))

    Lv0ax.set_xticklabels([])
    Lv0ax.grid()
    Tempax.grid()

    Lv0ax.set_ylabel('Level 0 Rate (Hz)')
    Tempax.set_ylabel('Tempature (C)')
    Tempax.set_xlabel('Time (UTC)')

    Lv0ax.set_xlim([times_x[0], times_x[-1]])
    Tempax.set_xlim([times_x[0], times_x[-1]])

    plt.show()

    save_movie = input('Save this plot? (Y/n): ')
    answers = ['Y', 'y', 'N', 'n']
    while save_movie not in answers:
        save_movie = input('Invalid response (Y/N): ')

    if save_movie == 'Y' or save_movie == 'y':
        start_time = times_x[0].strftime('%H-%M-%S')
        end_time = times_x[-1].strftime('%H-%M-%S')

        save_path = Path(__file__).resolve().parents[2] / 'Plots/OneD' / f'{times_x[0].date()}'
        if not save_path.is_dir():
            Path.mkdir(save_path)

        fig.savefig(Path(save_path / f'{start_time}_{end_time}.png'))

if __name__ == '__main__':

    # For testing purposes only
    date = DataDate('130511', Detectors())
    getDataForOneD(date, '1415', dt.datetime.strptime('10:00:00', '%H:%M:%S'), dt.datetime.strptime('13:00:00', '%H:%M:%S'), dt.datetime.strptime('12:20:00', '%H:%M:%S'))
