import os
from CoreRateLv0 import *

path = "DataDates"
start = False

for filename in os.listdir(path):
    if filename == "190422":
        start = True
    if start:
        print("----------------------------")
        print("\nCreating " + str(filename))
        MakePlots(filename, True)
        print("\nDone " + str(filename))
        print("============================")
