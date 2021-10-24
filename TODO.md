# ToDo

- On inital run of CRAT check that RawData is properly configured
  - Make sure Raw_NLDN.txt exists and at least one file in L0L1 exists of format l0_10min_##.txt
- When loading a date/year that no L0 data exists for, warn user (specifically if there is not a L0 year data file for it)
  - Could check to see if there is data in the L0 buffer of the dataDate after loading
- ~~Fix stopping error when loading dataDate with folder and no data sheets~~
  - ~~Specifically check the L0L1.txt/NLDN.txt existance rather than just the folder~~
  - Check this functionality
- Dont force rawData load when loading years that you may have already processed previously
- Funcitonality to see warnings of data
  - Something with the _warn already added in dataDates and dataDate
- Generalize the getDataForOneD when no start/end times are input, the whole day is assumed
- Generalize OneDimension functions for all times and normalize to outer-most times of granularity 10min
- Generalize time granularity accross the board
  - Have a file for program settings including the time granularity, maybe warnings
- loadDates command in CRAT
  - Employ the loadDates function in dataDates, just need to configure input to be of type list
- Maybe split the animate function in dataDates to getData and animateData like OneDimension plots
