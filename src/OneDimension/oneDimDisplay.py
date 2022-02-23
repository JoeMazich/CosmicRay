import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

root_file = r'{}'.format(Path(__file__).resolve().parents[1])
sys.path.append(root_file)

import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from dataDate import DataDate, KeyLv0
from detectors import Detectors

TIME_GRANULARITY = dt.timedelta(minutes=10)

# Get the oneD data with regard to the self-explainoroty parameters (times are inclusive on both sides)
def getDataForOneD(dataDate: DataDate, detector_number: str, start_time: dt.time, end_time: dt.time):

    looking_time = start_time
    times_x, level0_y, tempature_y, level0_errors = [], [], [], []

    while looking_time <= end_time:
        event_datetime = dt.datetime.combine(dataDate.date.date(), looking_time.time())
        try:
            key = KeyLv0(event_datetime, detector_number)
            level0 = dataDate[key].lv0
            tempature = dataDate[key].tempature

            if tempature < -100:
                raise Exception

            times_x.append(key.event_datetime)

            level0_y.append(level0)
            tempature_y.append(tempature)

            error = ( 1 / math.sqrt( level0 * 60 * 10 ) ) * level0
            level0_errors.append(error)
        except Exception as e:
            pass

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


def plotLv0vsTemp(level0s: List[float], tempatures: List[float]) -> None:

    level0, tempature = [], []

    # getting the data given to use more readable
    for ts, ls in zip(tempatures, level0s):
        assert len(ts) == len(ls)
        for t, l in zip(ts, ls):
            if (t and l):
                tempature.append(t)
                level0.append(l)

    tempature_avg = sum(tempature)/len(tempature)

    # setting up the figure
    fig = plt.figure(figsize=(10, 10))
    #fig.suptitle("Normalization ...", fontsize=20)
    gs = fig.add_gridspec(1, 2, left=0.12, right=0.93, top=0.93, bottom=0.05, wspace=0.2, hspace=0.07)

    # first plot ( the pre-normalized plot)
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title("Original")

    # plot all the points as well as calc the best fit line
    ax.scatter(tempature, level0)
    theta = np.polyfit(tempature, level0, 1)
    best_fit = theta[1] + theta[0] * np.asarray([max(tempature), min(tempature)]) #np.asarray(tempature)

    # calc the y average based on the temp average for later
    y_avg = tempature_avg * theta[0] + theta[1]

    # plot the best fit line
    ax.plot([max(tempature), min(tempature)], best_fit, '#FF0080')
    ax.set_ylim([770, 860])
    #ax.plot(tempature, best_fit, '#FF0080')

    #x_point = min(tempature)

    # THIS IS THE NORMALIZATION PROCESS THAT WILL NEED TO BE CHANGED
    expected_l = [] # this is the list that will be plotted for y aganist the normal x
    for t, l in zip(tempature, level0):
        y_2 = t * theta[0] + theta[1]
        percent_change = (y_2 / y_avg)
        expected_l.append(l / percent_change)

    # make the normalized graph plot
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_title("Normalized")
    ax2.set_ylim([770, 860])

    # plot it and find its best fit line
    ax2.scatter(tempature, expected_l)
    theta = np.polyfit(tempature, expected_l, 1)
    best_fit = theta[1] + theta[0] * np.asarray([max(tempature), min(tempature)])
    ax2.plot([max(tempature), min(tempature)], best_fit, '#FF0080')

    #plt.xlabel('Tempature (C)')
    #plt.ylabel('Level 0 Rate (Hz)')

    # show it
    plt.show()

    # commented out saving functionality
    '''
    save_movie = input('Save this plot? (Y/n): ')
    answers = ['Y', 'y', 'N', 'n']
    while save_movie not in answers:
        save_movie = input('Invalid response (Y/N): ')

    if save_movie == 'Y' or save_movie == 'y':

        save_path = Path(__file__).resolve().parents[2] / 'Plots/Normalization'
        if not save_path.is_dir():
            Path.mkdir(save_path)

        fig.savefig(Path(save_path / f'test.png'))
    '''

def plotHans(dataDate: DataDate, near_detectors: Dict, size: int, start_time: dt.time, end_time: dt.time) -> None:

    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(dataDate.date.strftime('%y%m%d'), fontsize=20)
    gs = fig.add_gridspec(size, size, left=0.12, right=0.93, top=0.93, bottom=0.05, wspace=0.2, hspace=0.07)

    anno_opts = dict(xy=(0.5, 0.9), xycoords='axes fraction', va='center', ha='center')

    start_time = dt.datetime.combine(dataDate.date, start_time.time())
    end_time = dt.datetime.combine(dataDate.date, end_time.time())

    for n in range(size):
        for m in range(size):

            data = getDataForOneD(dataDate, near_detectors[n, m], start_time, end_time)

            ax = fig.add_subplot(gs[n, m])

            ax.set_xlim([start_time, end_time])
            ax.set_ylim([723, 745])

            if m != 0:
                ax.set_yticks([])
            if n != size - 1:
                ax.set_xticks([])

            ax.annotate(near_detectors[n, m], **anno_opts)
            ax.plot(data[0], data[1], lw=1, c='green')

    plt.show()

if __name__ == '__main__':

    # For testing purposes only
    date = DataDate('130511', Detectors())
    getDataForOneD(date, '1415', dt.datetime.strptime('10:00:00', '%H:%M:%S'), dt.datetime.strptime('13:00:00', '%H:%M:%S'), dt.datetime.strptime('12:20:00', '%H:%M:%S'))
