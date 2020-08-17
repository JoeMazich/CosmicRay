import os
interesting_dates = []

file = open('RawData/NLDN/Raw_NLDN.txt', 'r')

# Needs a rewrite
# Delete all files first

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

for line in file:
    columns = line.split()

    if abs(float(columns[4])) > 100 and Date_C2P(columns[0]) not in interesting_dates:
        interesting_dates.append(Date_C2P(columns[0]))

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
