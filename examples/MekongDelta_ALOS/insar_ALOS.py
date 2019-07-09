import numpy as np
import pandas as pd 
import os,sys,subprocess
import InsarFlowObj as isfo
import InsarFlowFunc as isfc

data = pd.read_csv('Mekong_ASF_ALOS.csv')
paths = np.unique(data['Path Number'])
frames = np.unique(data['Frame Number'])
sar = pd.DataFrame(np.vstack([frames]*len(paths)).T, columns=paths)

# Frames not running (outside Mekong Delta) are set to NaN
#   477: [NaN,NaN,180,190,200]
#   478: [NaN,170,180,190,200]
#   479: [NaN,170,180,190,200]
#   480: [160,170,180,190,200]
#   481: [160,170,NaN,NaN,NaN]
sar.loc[0:2,477]=np.nan
sar.loc[0,478]=np.nan
sar.loc[0,479]=np.nan
sar.loc[2:5,481]=np.nan

#########################################################################
# In this Mekong example, we only process 2 frames (477-180 & 477-190)
# that cover a small area of the Delta.
# First, set all frames to Nan, then set the values for frames processed
#########################################################################
for col in sar.columns:
    sar[col] = np.nan
sar.loc[2,477]=180
sar.loc[3,477]=190


isce = True        # Set True if you run ISCE processing
giant = False       # Set True iff you finished ISCE and run GIAnT

# Run ISCE processing first.
if isce:
    """
    SET OPTIONS FOR RUNNING ISCE ...........................
    Change mode and options of flag_ALOS for your processing.
    """
    flag_ALOS = isfo.ALOS_Options( 
                Mode = 'insar',                 # Processing mode, select 'insar' or 'stripmap'
                DownloadImages = 'true',       # L1.0 data will be download from ASF website
                UnzipData = 'true',            # data will be uncompressed
                BaselineCheck = 'true',         # a baseline check will be done to create pairs
                RemoveUnsedPairs = 'true',      # all non-satisfied pair folders will be remove.
                GenerateXML = 'true',           # Generate xml files for each IFG folders for ISCE processing
                RunIFGs = 'true',               # Run ISCE for processing
                GenerateRoipac = 'true',       # Create Roipac files for GIAnT runs
                CleanFiles = 'true',           # Remove all files that are not used in GIAnT
                TempBslnThres = 1500,           # Unit [day]
                PerpBslnThres = 730,            # Unit [m]
                OpenMP_Num_Threads = 40         # Number of threads used in OpenMP for ISCE.
                )
    """
    LIST OF FILES AND FOLDERS GENERATED DURING ISCE PROCESSING
    Users are recommended to use default names as shown below.
    """
    list_ALOS = isfo.ALOS_Lists( 
                LogFiles = 'log_Alos.txt',          # Log file
                dateID = 'dateID.info',             # File containing date info of ALOS images
                LogScreen = 'screen.log',           # Screen log of isce apps
                ALOSScenes = 'ALOS_scenes.info',    # File containing ALOS scene
                DatePairList = 'datePair.info',     # File includes pairs that are formed by BaselineCheck
                ActiveList = 'ifgs_active.info',    # List of active (incomplete) pairs 
                CompleteList = 'ifgs_complete.info',# List of complete pairs
                BoundBox = 'boundbox.list',         # Bounding Box of the region
                IfgList = 'ifg.list',               # Ifg list for GIANT
                SubData = 'subdata.csv',            # Subdata extracted from master CSV file
                ZipDirectory = 'ALOS_zip',          # Folder contains zip ALOS files
                RawDirectory = 'ALOS_raw',          # Folder for ALOS raw extraction
                ISCEDirectory = 'INSAR',            # Folder for ISCE output processing
                GIAnTDirectory = 'GIAnT'            # Folder used for GIAnT processing
                )

    create_parameters = True                        # Generate Config Files
    run_script = True                               # Run the Bash script

    # Create config files in each Path & Frame folder
    isfc.AlosCreateConfigs(data, sar, flag_ALOS, create_parameters,list_ALOS)

    # Run the bash script
    isfc.AlosRunISCEScripts(sar, run_script, list_ALOS)


# After finishing ISCE, run GIAnT for time-series analysis
if giant:
    prep = True
    igram = True
    processtack = True
    invert = True
    gmode = 'nsbas'   # sbas or nsbas
    isfc.RunGIAnTScripts(sar, prep, igram, processtack, invert, gmode)
