import geopy
import numpy as np
from geopy.distance import geodesic
from pathlib import Path

###################
# global parameters
###################

ZCLF   = 1.382
LATCLF = 39.29693
LONCLF = -112.90875
NTASD  = 510
REARTH = 6371

####################
def gps2cart(gnnnn):
####################

# convert from gps lat/lon to CLF-centered cartesian

    g0000   = geopy.point.Point(39.29693,-112.90875,0)#ZCLF)
    g0000eq = geopy.point.Point(0.0,g0000.longitude,0)#g0000.altitude)
    gnnnneq = geopy.point.Point(0.0,gnnnn.longitude,0)#gnnnn.altitude)

    r = (geodesic(g0000,gnnnn).km)
    y = (geodesic(gnnnn,gnnnneq).km)-(geodesic(g0000,g0000eq).km)

    if gnnnn.longitude > g0000.longitude:
        x =  np.sqrt(r*r-y*y)
    else:
        x = -1.0*np.sqrt(r*r-y*y)
    z = gnnnn.altitude

    return x,y,z

##################
def cart2gps(x,y):
##################

    x[:] = [ LONCLF+(xx/(REARTH*np.sin((90.0-LATCLF)*(np.pi/180.0))))*(180.0/np.pi) for xx in x]
    y[:] = [ LATCLF+(yy/REARTH)*(180.0/np.pi) for yy in y]

###############################
def tasdxyz(tasdnum1,tasdx,tasdy,tasdz):
###############################

# read sd locations from file
    ff=open(Path(__file__).resolve().parent / 'tasd_gpscoors.txt','r')
    tasdnum = []
    tasdlat = []
    tasdlon = []
    tasdalt = []

    for line in ff:
        line = line.strip()
        columns = line.split()
        tasdnum.append(float(columns[0]))
        tasdlat.append(float(columns[1]))
        tasdlon.append(float(columns[2]))
        tasdalt.append(0.001*float(columns[3]))


    ff.close()


# convert sd lat/lon to CLF cartesian

    for i in range(0,NTASD):
        gsd = geopy.point.Point(tasdlat[i],tasdlon[i],0)#tasdalt[i])
        sdx,sdy,sdz = gps2cart(gsd)
        tasdx.append(sdx)
        tasdy.append(sdy)
        tasdz.append(sdz)
        tasdnum1.append(tasdnum)
#####################################
def tasdgps(tasdlat,tasdlon,tasdalt):
#####################################

# read sd locations from file

    ff=open(Path(__file__).resolve().parent / 'tasd_gpscoors.txt','r')
    tasdnum = []

    for line in ff:
        line = line.strip()
        columns = line.split()
        tasdnum.append(float(columns[0]))
        tasdlat.append(float(columns[1]))
        tasdlon.append(float(columns[2]))
        tasdalt.append(0.001*float(columns[3]))

    ff.close()

####################
def ivanov2clf(x,y):
####################

    x[:] = [(xx-12.2435)*1.200 for xx in x]
    y[:] = [(yy-16.4406)*1.200 for yy in y]

####################
def clf2ivanov(x,y):
####################

    x[:] = [(xx/1.200+12.2435) for xx in x]
    y[:] = [(yy/1.200+16.4406) for yy in y]
