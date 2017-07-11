# Date: March 7 2017

# If you want to run only on FP17, remove FP18 from continuousVarNames = ["FP17", "FP18"] (line 37)
# and comment out this part: (line 247-261):
##################################
# Subtract normalized by Vectors #  
##################################

#############################################
# For all files in a given folder:          #
# Script creates new continuous variables   # 
# with names ending with:                   #
# _80Hz                                     #
# _normalized                               #
# _normalizedByVector                       #
# _DiffByVect                               #
# and a new Event in Timestamps:             #
# PeaksFP17_normByV                         #
#                                           #
# Finally, it saves the output into files   #
# that will have name ending with _Analyzed #
#############################################


import nex
import math

################
# Parameteres #
################

# specify your file filter here
fileFilter = "C:\\Users\\kravitzlab\\Documents\\Ilona\\NE2016\\ExamplePLXfiles\\*.plx"


# modify variable name
continuousVarNames = ["FP17","FP18"]
herz = "_80Hz"
# variable names to calculate difference (17-18)
continuousVarName1 = "FP17_normalizedByVector"
continuousVarName2 = "FP18_normalizedByVector"
# name of a new variable containing differences (17-18)
newcontinuousVarName = "DiffByVect"
# modify template name
templateName = 'LexSpectrogram80'
# name of new variables containing peaks
newEventName = "PeaksFP17_normByV"
filteredPeaks = "FilteredPeaks"

# define first point index for normalizing Vector
firstIndex = 600

# define bottom to reduce the data being used to the bottom % of the values
bottom  = 0.25

# define time interval for local peaks(in number of lines)
my_bin = 100 # sampling at 1Khz means value of 1000 looks for local maxima 1 second apart
treshold = 5 # local max above this treshold
delay = 20 # delay between peaks to filter 

# ending of the output group of files
ending = "_Analyzed.nex"

##############
# functions #
##############

# function to calculate standard deviation from a given list
def my_std_dev(my_list):
    temp = 0
    average = sum_sth(my_list)/len(my_list)
    for i in range(len(my_list)):
        temp = temp + math.pow((my_list[i]-average), 2)
    std_dev = math.sqrt(temp)/math.sqrt(len(my_list)-1)
    return average, std_dev
    
# function to sum on what standard sum doesn't work
def sum_sth(some_list):
    sum_all = 0
    for el in some_list:
        sum_all = sum_all + el
    return sum_all
    
# function to normalize
def normalize(el,mean,dev):
    return (el-mean)/dev

# function to create destination path 
# name of output file appends _Analyzed
def getNewPath(sourcePath):
    pathElements = str(sourcePath).split('\\')
    oldPath = "\\".join(pathElements[0:-1])+"\\"
    origName = pathElements[-1].split('.')
    newPath = oldPath+origName[0]+ending
    return newPath

###########
# Execute #
###########


# GetFileCount will store (internally) names of the files that match the filter
n = nex.GetFileCount(fileFilter)

for i in range(n):
    # get a matching file name (recognizes indexes from 1)
    fileName = nex.GetFileName(i+1)
    
    # open the file
    doc = nex.OpenDocument(fileName)
    
    # if file was opened successfully
    if doc > 0:
        
        print "Opened ",fileName
        
        nex.DeselectAll(doc)

        for n in range(len(continuousVarNames)):
            nex.Select(doc,doc[continuousVarNames[n]])

            # calculate spectrograms
            nex.ApplyTemplate(doc, templateName)

            # we need analysis parameters values to specify times
            startTime = float(nex.GetTemplateParValue(templateName, 'Start (sec)'))

            # find new var sampling rate
            shift = float(nex.GetTemplateParValue(templateName, 'Shift (sec)'))
            samplingRate = 1.0/shift
    
            # get numerical results column names
            colNames = doc.GetNumResColumnNames()
            # skip first column if it contains frequency values
            firstColumn = 0
            if colNames[0] == 'Frequency Values':
                firstColumn = 1
        
            # add values to new variable
            numRes = doc.GetAllNumericalResults()    
    
            # create new variable
            newVarName = continuousVarNames[n] + herz
            doc[newVarName] = nex.NewContVarWithFloats(doc, samplingRate)
    
            for col in range(firstColumn, len(numRes)):
                sum = 0
                for row in range(len(numRes[col])):
                    sum += numRes[col][row]
                average = sum/float(len(numRes[col]))
                nex.AddContValue(doc[newVarName], startTime + (col-firstColumn)*shift, average )

            print newVarName    # created a variable _80Hz from FP17 and FP18 values
    
#############################################
# Create new normalized continuous variable #  # from values of _80Hz variable
#############################################
  
            nex.DeselectAll(doc)

            # get variables 2 normalize
            timestamps2normalize = doc[newVarName].FragmentTimestamps()
            values2normalize = doc[newVarName].ContinuousValues()

    
######################
# Normalizing Vector #
######################

            ##################################################################################
            # Modification to reduce later "false" peaks for GFP mice

            # 1. sort values2normalize ascending
            # 2. find length of original list, and e.g. 25% of that value
            # 3. reduce the data being used to the bottom 25% of the values:
            # 4. use my_std_dev on the new list
            # remember not to modify the original values2normalize because 
            # we need them to plot continuous variable later. Example:

            # original = [1,4,3,6,8]
            # original2use = original[:]
            # original2use.sort()

            # print("original:",original)
            # print("sorted:",original2use)

            # Result: original: [1, 4, 3, 6, 8], sorted: [1, 3, 4, 6, 8]

#########################################################################################################################
# New modification. First subtract local means from all values in _80Hz.
# Then, on that list perform z score, using avg and std dev calculated from the reduced list


            # create lists of local means
            V_means = []

            for i in range(len(values2normalize)):
                if (i > firstIndex and i <= (len(values2normalize)-firstIndex)):
                    temp_list = values2normalize[(i-firstIndex):(i+firstIndex)]
                    loc_mean = sum_sth(temp_list)/len(temp_list)
                    V_means.append(loc_mean)
                    
            # create a list of variables that are equal to values from _80Hz-local mean
            NewHzValuesMinusLocalMean = []
            
            # for the first x min apply first element from means
            # for the last x min apply last element from means
            for i in range(len(values2normalize)):
                if (i <= firstIndex):
                    V_reduced = (values2normalize[i] - V_means[0])
                elif (i > len(values2normalize)-firstIndex):
                    V_reduced = (values2normalize[i] - V_means[-1])
                else:
                    V_reduced = (values2normalize[i] - V_means[i-firstIndex-1])
                NewHzValuesMinusLocalMean.append(V_reduced)
             
             
            # calculate reduced avg and reduced sdt dev from intermediate list(_80Hz-localMeans)
            sorted_values = NewHzValuesMinusLocalMean[:]
            sorted_values.sort()
            # calculate the numberof values required
            #print sorted_values[1:10]
            len_of_new_list = len(NewHzValuesMinusLocalMean) * bottom
            # save reduced list to calculate std dev
            reduced = sorted_values[:int(len_of_new_list)]
            
            # get average and standard deviation values for voltages, calculated from the reduced list of 
            # intermediate values (list(_80Hz-localMeans))
            my_avg, my_std = my_std_dev(reduced)
            
            # create a new variable and add new continuous variable
            normalizedByVector = continuousVarNames[n] + "_normalizedByVector"
            doc[normalizedByVector] = nex.NewContVarWithFloats(doc, samplingRate)
            
            # for all values in NewHzValuesMinusLocalMean perform z score using avg and std dev from reduced list
            for i in range(len(NewHzValuesMinusLocalMean)):
                zScored = (NewHzValuesMinusLocalMean[i] - my_avg)/my_std
                nex.AddContValue(doc[normalizedByVector],timestamps2normalize[i],zScored)
        
            print normalizedByVector 

############################

        timestamps4newVar = doc[continuousVarName1].Timestamps()
        values2subtract1 = doc[continuousVarName1].ContinuousValues()
        
##################################
# Subtract normalized by Vectors #  # Difference (if you want to run it just for FP17 comment this part out, after removing "FP18" from continuousVarNames = ["FP17", "FP18"])
##################################

        # create new variable
        doc[newcontinuousVarName] = nex.NewContVarWithFloats(doc, samplingRate)
        # get variables to subtract 

        values2subtract2 = doc[continuousVarName2].ContinuousValues()

        for i in range(len(values2subtract1)):
            diff = values2subtract1[i]-values2subtract2[i]
            nex.AddContValue(doc[newcontinuousVarName], timestamps4newVar[i], diff) 

        print newcontinuousVarName

####################################
# Create Peak Event in Timestamps #
####################################

        # create a new column in Timestamps
        doc[newEventName] = nex.NewEvent(doc, 0)
        # select a column to add timestamps
        eventVar = nex.GetVarByName(doc, newEventName)

        # how many local sections are there
        bin_No = int(len(values2subtract1)/my_bin)
        start_i = 0
        next_i = 0
        initial_peaks = []
        filtered = []
        for i in range(bin_No):
            start_i = next_i
            next_i = start_i + my_bin
            temp_list = values2subtract1[start_i:next_i]
            loc_max = max(temp_list)
            if (loc_max > treshold):
                indexes = [loc_i for loc_i, j in enumerate(temp_list) if j==loc_max]
                for el in indexes: # in case there are more than one the same max values
                    # take account of global position
                    el = el + i*my_bin
                    # add relevant timestamp to Timestamps
                    initial_peaks.append(timestamps4newVar[el])
                    if (el != 0):
                        nex.AddTimestamp(eventVar, timestamps4newVar[el])
            
        print newEventName
        
        # create a new column in Timestamps
        doc[filteredPeaks] = nex.NewEvent(doc, 0)
        # select a column to add timestamps
        nextEventVar = nex.GetVarByName(doc, filteredPeaks)

        # write filtered peaks into event
        for i in range(len(initial_peaks)):
            if (i==0):
                filtered.append(initial_peaks[i])
            else:
                if ((initial_peaks[i] - initial_peaks[i-1]) > delay):
                    filtered.append(initial_peaks[i])
                    nex.AddTimestamp(nextEventVar, initial_peaks[i])
                    
        print filteredPeaks
        print
        
        # save file in .nex format as fileName_Analyzed
        nex.SaveDocumentAs(doc, getNewPath(fileName))

        # close the document
        nex.CloseDocument(doc)
        
    else:
        print "Could not open ", doc