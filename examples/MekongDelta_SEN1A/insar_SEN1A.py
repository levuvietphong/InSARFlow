import numpy as np
import pandas as pd 
import os,sys,subprocess
import InsarFlowObj as isfo
import InsarFlowFunc as isfc

fileASF = 'MekongUpper_S1A.csv'
auxlink = 'https://qc.sentinel1.eo.esa.int/product/S1A/AUX_CAL/20190228T092500/S1A_AUX_CAL_V20190228T092500_G20190227T100607.SAFE.TGZ'
project_name = os.path.splitext(fileASF)[0]
data = pd.read_csv(fileASF)
platform=np.unique(data['Platform'])[0]
pathnum=np.unique(data['Path Number'])[0]
framenum = np.unique(data['Frame Number'])
sar = pd.DataFrame({pathnum:framenum})

isce = True         # Set True if you run ISCE processing (must activate ISCE env)
giant = False       # Set True iff you finished ISCE and run GIAnT (must activate GIAnT env)

# Run ISCE processing first.
if isce:
    """
    SET OPTIONS FOR RUNNING ISCE ...........................
    """
    opts_SEN1A= isfo.SEN1A_Options( 
                DownloadImages = 'true',       # SLCs data will be download from ASF website
                SelectRegion = 'true',          # Select specific region for processing                
                GenerateXML = 'true',          # Create XML files for isce processing
                RunIFGs = 'true',              # Run ISCE for processing
                GenerateRoipac = 'true',       # Create Roipac files for GIAnT runs
                CleanFiles = 'true',           # Remove all files that are not used in GIAnT (No need for SEN1A)
                TempBslnThres = 30,             # Unit [day]
                OpenMP_Num_Threads = 40         # Number of threads used in OpenMP for ISCE.
                )
    
    # Select region of interest
    # If not specified, a common region among all images will be selected
    if opts_SEN1A.SelectRegion == 'true':
        opts_SEN1A.minLatitude = 9.0
        opts_SEN1A.maxLatitude = 10.0
        opts_SEN1A.minLongitude = 105.0
        opts_SEN1A.maxLongitude = 106.0



    """
    LIST OF FILES AND FOLDERS GENERATED DURING ISCE PROCESSING
    Users are recommended to use default names as shown below.
    """
    list_SEN1A= isfo.SEN1A_Lists( 
                Project = project_name,                 # Folder name of the project
                Platform = platform,                    # Type of SAR data
                LogFiles = 'log_sen1A.txt',             # Log file
                AuxLink = auxlink,                      # Link for downloading aux file
                LogScreen = 'screen.log',               # Screen log of isce apps
                DatePairList = 'list_ifgs_full.info',   # File includes pairs that are formed by BaselineCheck
                ActiveList = 'ifgs_active.info',        # List of active (incomplete) pairs 
                CompleteList = 'ifgs_complete.info',    # List of complete pairs
                BoundBox = 'boundbox.list',             # Bounding Box of the region
                IfgList = 'ifg.list',                   # Ifg list for GIANT
                SubData = 'subdata.csv',                # Subdata extracted from master CSV file
                SLCDirectory = 'SLCs',                  # Folder contains SLCs data
                AuxDirectory = 'AUXILIARY',             # Folder contains Auxliary data
                PoeDirectory = 'POEORB',                # Folder contains POEORB data
                ISCEDirectory = 'ISCE',                 # Folder for ISCE output processing
                GIAnTDirectory = 'GIAnT'                # Folder used for GIAnT processing
                )

    create_parameters = True                        # Generate Config Files
    run_script = True                               # Run the Bash script

    # Create config files in each Path & Frame folder
    isfc.Sen1ACreateConfigs(data, opts_SEN1A, create_parameters, list_SEN1A)

    # Run the bash script
    isfc.Sen1ARunISCEScripts(run_script, list_SEN1A)


# After finishing ISCE, run GIAnT for time-series analysis
if giant:
    print('Running GIAnT for timeseries analysis!!!')
    prep = True
    igram = True
    processtack = True
    invert = True
    gmode = 'sbas'   # sbas or nsbas    
    isfc.RunGIAnTScripts(project_name, platform, sar, prep, igram, processtack, invert, gmode)