-------------------------------
| NormalizingVectorFromFolder |
-------------------------------

Does everything for all files in a given folder, 
and saves the analyzis into a new file that has the same name as 
the original + _Analyzed.nex

1.
It applies given template to both FP17 or FP18 continuous variables
and creates a new, filtered continuous variables _80Hz (change this in th beginning of the code
if your template is set to different frequency to get the accurate name of the new variable)
2.
First subtract local means from all values in _80Hz.
Create a list of variables that are equal to values from _80Hz-local mean.
Calculate reduced avg and reduced sdt dev from intermediate list(_80Hz-localMeans).
Get average and standard deviation values for voltages, calculated from the reduced list of 
intermediate values (list(_80Hz-localMeans)).
my_avg, my_std
For all values in NewHzValuesMinusLocalMean perform z score using avg and std dev from reduced list.
(NewHzValuesMinusLocalMean[j] - my_avg)/my_std
New continuous variable _normalizedByVector is created
3.
It subtracts values of FP18_normalizedByVector from FP17_normalizedByVector (FP17-FP18), 
and saves results in a new DiffFP17ByVectFP18byVect continuous variable
4.
It searches for local peaks in FP17_normalizedByVector continuous variable that are above the defined treshold.
Next, it saves the timestamps for those peak values into the "PeaksFP17_normByV" event in Timestamps
5.
It filters above (PeaksFP17_normByV) peaks to select only those that are separated by 
the time period greater than defined delay variable.
It saves filtered timestamps as FilteredPeaks event.

-------------
| SavePeaks |
-------------

Does everything for all files in a given folder, 
and saves the results into a new file that has the same name as 
the original + _peaks.nex


It searches for local peaks in FP17_normalizedByVector continuous variable that are above the defined treshold.
Next, it saves the timestamps for those peak values into the "Peak" event in Timestamps.


