import os
from datetime import *
interesting_dates = []

start_date = input('where should I start searching from (date)? ')
end_date = input('where should I stop searching (dates)? ')
nldn_activity_limit = int(input('What is the minimum nldn peak current (kA) needed to count? '))

ONE_DAY = timedelta(days=1)

def Date_C2P(date):
    temp = date.split("-")
    year = int(temp[0]) - 2000
    month = int(temp[1])
    day = int(temp[2])
    return str(year*10000 + month*100 + day).rjust(6, "0")

def Date_P2C(date):
    year = str(int(date[0:2]) + 2000)
    month = date[2:4]
    day = date[4:6]
    return year + "-" + month + "-" + day

def Date_P2D(plain_date):
    year = 2000 + int(plain_date[0:2])
    month = int(plain_date[2:4])
    day = int(plain_date[4:6])
    return date(year, month, day)

def Date_C2D(cut_date):
    temp = cut_date.split("-")
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    return date(year, month, day)

def add_date(date):
    if date not in interesting_dates:
        interesting_dates.append(date)


current_date = Date_P2D(start_date)

file = open('RawData/NLDN/Raw_NLDN.txt', 'r')

for line in file:
    columns = line.split()
    line_date = Date_C2D(columns[0])

    if current_date > line_date:
        pass
    elif current_date == line_date and (abs(float(columns[4])) > nldn_activity_limit):
        add_date(current_date)
        current_date + ONE_DAY
    elif current_date < line_date and line_date <= Date_P2D(end_date) :
        current_date = line_date
        add_date(current_date)
        current_date + ONE_DAY

    if current_date >= Date_P2D(end_date):
        break

file.close()

print(interesting_dates)

'''
for date in interesting_dates:
    if not os.path.isdir("DataDates/" + date):
        os.mkdir("DataDates/" + date)


Parentfile = open('RawData/NLDN/over100.txt', 'r')

for line in Parentfile:
    columns = line.split()
    date = Date_C2P(columns[0])

    if date in interesting_dates:
        Datefile = open('DataDates/' + date + '/NLDNOver100.txt', 'a')
        Datefile.write(line) #line
        Datefile.close()
Parentfile.close()
'''
'''
for filename in os.listdir("RawData/L0L1/"):
    Parentfile = open('RawData/L0L1/' + filename, 'r')

    for line in Parentfile:
        columns = line.split()
        if len(columns) == 0:
            print(filename)
        date = columns[0]

        if date in interesting_dates:
            Datefile = open('DataDates/' + date + '/L0L1.txt', 'a')
            Datefile.write(line) #line
            Datefile.close()
    Parentfile.close()
'''
