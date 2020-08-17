import os

path = "RawData/NLDN/"

unsorted_filename = "nldnmerged.dat"
Correctedfilename = "Raw_NLDN.txt"

list = []

file = open(path + unsorted_filename, 'r')

for line in file:
    columns = line.split()
    str = " "
    if len(columns) == 6:
        list.append(str.join(columns))
    if len(columns) == 10:
        if columns[5] == "C" or columns[5] == "G":
            list.append(str.join(columns[0:6]))
        elif columns[9] == "C" or columns[9] == "G":
            temp = columns[0:5]
            temp.append(columns[9])
            list.append(str.join(temp))
file.close()

file = open(path + Correctedfilename, 'w')

for line in list:
    file.write(line)
    file.write('\n')

file.close()
