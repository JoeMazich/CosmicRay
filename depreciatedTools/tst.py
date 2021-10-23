import os

def Date_C2P(date):
    temp = date.split("-")
    year = int(temp[0]) - 2000
    month = int(temp[1])
    day = int(temp[2])
    date = str(year*10000 + month*100 + day).rjust(6, "0")
    return date, year, month, day

dates = {}

Parentfile = open('RawData/NLDN/nldnmerged.dat', 'r')
for line in Parentfile:
    columns = line.split()
    date, year, month, day = Date_C2P(columns[0])
    peak_current = abs(float(columns[4]))

    if (month == 12 or month == 1 or month == 2):
        if date in dates:
            dates[date] += 1
        else:
            dates[date] = 1

Parentfile.close()

for date, count in dates.items():
    if count == 1:
        print(date)

print(dates.keys())
