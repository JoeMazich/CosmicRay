import matplotlib.pyplot as plt

bins = 50

C_bins = bins
G_bins = bins

file = open('RawData/NLDN/nldnmerged.dat', 'r')
C_NLDN, G_NLDN = [], []
print()
print("Date       | Time               | PC     | Type")
print("-----------------------------------------------")

for line in file:
    columns = line.split()
    if abs(float(columns[4])) > 100 and columns[5] == "C":
        print(columns[0] + " | " + columns[1] + " | " + columns[4] + " | " + columns[5])

    if columns[5] == "C":
        C_NLDN.append(float(columns[4]))
    elif columns[5] == "G":
        G_NLDN.append(float(columns[4]))

file.close()


fig = plt.figure()
plt.rc('xtick', labelsize = 6)
plt.rc('ytick', labelsize = 6)
ax = fig.add_subplot()
ax.set_xticks([-700, -600, -500, -400, -300, -200, -100, 0, 100, 200, 300, 400])
ax.hist(G_NLDN, bins=G_bins,histtype='step', log=True, label='G Events')
ax.hist(C_NLDN, bins=C_bins,histtype='step', log=True, label='C Events')
leg = ax.legend()
fig.suptitle("NLDN Distribution from 2008 to 2019", fontsize=15)
plt.title(str(bins) + " bins")

plt.show()
