# CosmicRay

Basic tools for cosmic ray visualization

# How to use

## Setup File paths

1. Clone this repo locally
2. Run the file *RUN_ME_FIRST.py*
3. Check to make sure that directories *DataDates*, *Movies*, and *RawData* have been created.

##  Get data

1. Log onto tadserv
2. Move into */scratch0/rasha/lv10rate/outFiles*
3. Copy contents locally, into *CosmicRay/RawData/L0L1*
4. Move into */scratch0/rasha/NLDN_data*
5. Copy *Raw_NLDN.txt* into *CosmicRay/RawData/NLDN*

## Parse dates

We need to extract the data we want from the raw data we have based on the dates we care about. This can be done with the *GetDateData.py* tool
1. Run *GetDateData.py*
2. Choose the date you want
3. Check that the date got a folder within *DataDates* (i.e. *DataDates/140927*)
4. Check that the date got NLDN data and L0L1 data

## Create Movies

1. Run CoreRateLv0.py
2. Choose the date you wish (It has to be parsed beforehand)
3. Let it run - it will output into *Movies/{date}*
