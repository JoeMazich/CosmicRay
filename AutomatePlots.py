import os
from CoreRateLv0 import *

path = "DataDates"
start = False

'''for filename in os.listdir(path):
    if filename == "190422":
        start = True
    if start:
        print("----------------------------")
        print("\nCreating " + str(filename))
        MakePlots(filename, True)
        print("\nDone " + str(filename))
        print("============================")'''

for filename in ['090125', '120121', '121203', '130127', '160218', '161216', '170109', '170110', '170111', '170220', '180206', '181201', '190117', '190118', '190228']:
    print("----------------------------")
    print("\nCreating " + str(filename))
    MakePlots(filename, True)
    print("\nDone " + str(filename))
    print("============================")
