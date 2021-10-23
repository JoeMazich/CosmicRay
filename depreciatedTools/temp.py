import os

path = "RawData/NLDN/"

unsorted_filename = "Raw_NLDN.txt"
Correctedfilename = "over100.txt"

list = []

file = open(path + unsorted_filename, 'r')

for line in file:
    columns = line.split()
    if abs(float(columns[4])) > 100:
        list.append(line)
file.close()

file = open(path + Correctedfilename, 'w')

for line in list:
    file.write(line)

file.close()
