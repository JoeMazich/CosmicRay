import os

def Date_C2P(date):
    temp = date.split("-")
    year = int(temp[0]) - 2000
    month = int(temp[1])
    day = int(temp[2])
    return str(year*10000 + month*100 + day).rjust(6, "0")

def GetDataDate(date):
    if not os.path.isdir("DataDates/" + date):
        os.mkdir("DataDates/" + date)

    '''
    Parentfile = open('RawData/NLDN/Raw_NLDN.txt', 'r')
    for line in Parentfile:
        columns = line.split()
        datePF = Date_C2P(columns[0])

        if datePF == date:
            Datefile = open('DataDates/' + date + '/NLDN.txt', 'a')
            Datefile.write(line)
            Datefile.close()
    Parentfile.close()

    if not os.path.isfile('DataDates/' + date + '/NLDN.txt'):
        open('DataDates/' + date + '/NLDN.txt', 'a')'''

    for filename in os.listdir("RawData/L0L1temp/"):
        #Parentfile = open('RawData/L0L1/' + filename, 'r')
        flag = False
        if filename[9:11] == date[0:2]:
            Parentfile = open('RawData/L0L1temp/' + filename, 'r')

            for line in Parentfile:
                columns = line.split()
                if (len(line) > 6):
                    datePF = columns[0]

                    if datePF == date:
                        #Datefile = open('DataDates/' + date + '/L0L1.txt', 'a')
                        if not os.path.isdir("DataDates/temp/" + date):
                            os.mkdir("DataDates/temp/" + date)
                        Datefile = open('DataDates/temp/' + date + '/L0L1.txt', 'a')
                        Datefile.write(line) #line
                        Datefile.close()
                        flag = True
            Parentfile.close()
        if flag:
            print('Found it')

if __name__ == '__main__':
    date = input("What date do you want to get data for? ")

    GetDataDate(date)