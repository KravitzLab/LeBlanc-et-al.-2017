# Date: February 27 2017

import nex

################
# Parameteres #
################

# specify your file filter here (folder and types of files: nex)
# hint1: some systems might be sensitive to spaces in names of folders (it is better to avoid spaces in path)
# hint2: some systems might require double backslashes instead of slashes in the path (C:\\ instead of C:\)
# if the script does not read ANY files from your path, check the above 2 hints
fileFilter = "C:\\Users\\kravitzlab\\Documents\\Ilona\\ExamplePLXfiles\\testpeaksfromfolder\\*.nex"

# variable name to search for peaks
continuousVarName = "FP17_normalizedByVector"
# name of a new variable containing peaks
newVarName = "Peaks"
filteredPeaks = "FilteredPeaks"
# define time interval (in number of lines)
my_bin = 100
treshold = 2 # local max above this treshold
delay = 20

# ending of the output group of files
ending = "_peaks.nex"

# function to create destination path 
# name of output file appends _Analyzed
def getNewPath(sourcePath):
    pathElements = str(sourcePath).split('\\')
    oldPath = "\\".join(pathElements[0:-1])+"\\"
    origName = pathElements[-1].split('.')
    newPath = oldPath+origName[0]+ending
    return newPath

#######################
# Create new variable #
#######################


# GetFileCount will store (internally) names of the files that match the filter
n = nex.GetFileCount(fileFilter)
print n
for i in range(n):
    # get a matching file name (recognizes indexes from 1)
    fileName = nex.GetFileName(i+1)
    
    # open the file
    doc = nex.OpenDocument(fileName)
    
    # if file was opened successfully
    if doc > 0:
        
        print "Opened ",fileName

        nex.DeselectAll(doc)
        nex.Select(doc,doc[continuousVarName])

        # get continuous variables to search for peaks 
        timestamps4newVar = doc[continuousVarName].Timestamps()
        values2search = doc[continuousVarName].ContinuousValues()

        # create a new column in Timestamps
        doc[newVarName] = nex.NewEvent(doc, 0)
        # select a column to add timestamps
        eventVar = nex.GetVarByName(doc, newVarName)

        # how many local sections are there
        bin_No = int(len(values2search)/my_bin)
        start_i = 0
        next_i = 0
        initial_peaks = []
        filtered = []

        # write initial peaks to the event
        for i in range(bin_No):
            start_i = next_i
            next_i = start_i + my_bin
            temp_list = values2search[start_i:next_i]
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
            
        # create a new column in Timestamps
        doc[filteredPeaks] = nex.NewEvent(doc, 0)
        # select a column to add timestamps
        nextEventVar = nex.GetVarByName(doc, filteredPeaks)

        # write filtered peaks into event
        for i in range(len(initial_peaks)):
            if (i==0):
                filtered.append(initial_peaks[i])
                nex.AddTimestamp(nextEventVar, initial_peaks[i])
            else:
                if ((initial_peaks[i] - initial_peaks[i-1]) > delay):
                    filtered.append(initial_peaks[i])
                    nex.AddTimestamp(nextEventVar, initial_peaks[i])
      
        # save file in .nex format as fileName_peaks
        nex.SaveDocumentAs(doc, getNewPath(fileName))

        # close the document
        nex.CloseDocument(doc)
        
    else:
        print "Could not open ", doc