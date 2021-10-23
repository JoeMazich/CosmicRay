import matplotlib.pyplot as plt
import numpy as np

bins = 50

C_bins = bins
G_bins = bins

file = open('RawData/NLDN/nldnmerged.dat', 'r')
C_NLDN, G_NLDN = [], []
print()
'''print("Date       | Time               | PC     | Type")
print("-----------------------------------------------")'''

for line in file:
    columns = line.split()
    '''if abs(float(columns[4])) > 100 and columns[5] == "C":
        print(columns[0] + " | " + columns[1] + " | " + columns[4] + " | " + columns[5])'''

    if columns[5] == "C":
        C_NLDN.append(float(columns[4]))
    elif columns[5] == "G":
        G_NLDN.append(float(columns[4]))

file.close()

C_mean = np.mean(np.asarray(C_NLDN))
G_mean = np.mean(np.asarray(G_NLDN))
total_mean = np.mean(np.asarray(G_NLDN + C_NLDN))

C_rms = np.sqrt(np.mean(np.asarray(C_NLDN)**2))
G_rms = np.sqrt(np.mean(np.asarray(G_NLDN)**2))
total_rms = np.sqrt(np.mean(np.asarray(G_NLDN + C_NLDN)**2))

print('Mean:', total_mean, '| RMS:', total_rms)

fig = plt.figure()
plt.rc('xtick', labelsize = 6)
plt.rc('ytick', labelsize = 6)
ax = fig.add_subplot()
ax.set_xticks([-700, -600, -500, -400, -300, -200, -100, 0, 100, 200, 300, 400])
ax.set_xlabel('Peak Current (kA)')
ax.set_ylabel('Number of Events')
ax.hist(G_NLDN, bins=G_bins, histtype='step', log=True, label='CG Events')
ax.hist(C_NLDN, bins=C_bins, histtype='step', log=True, label='IC Events')
'''ax.plot([total_mean, total_mean], [0, 100000], linewidth=0.5, label='Mean')
ax.plot([total_rms, total_rms], [0, 100000], linewidth=0.5, label='RMS')
ax.set_ylim(0, 100000)'''
leg = ax.legend()
fig.suptitle("NLDN Distribution from 2008 to 2019", fontsize=15)
'''plt.title('Mean: ' + str(total_mean) + ' | RMS: ' + str(total_rms))'''

print(C_mean, G_mean)
print(C_rms, G_rms)

# find mean and rms for C and for G sigma?
# y axis peak current kiloampare and x axis number of events title
# find the 5% days with no temp correlation
# pressure stuff maybe too in the future

plt.show()
