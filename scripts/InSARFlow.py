#!/usr/bin/env python

import numpy as np
import pandas as pd 
import os,sys,subprocess
import argparse, configparser
import InSARFlowObjs as isfo
import InSARFlowFuncs as isfc
import InSARFlowGIAnT as isfg

"""
--------------------------------------
Main processing function of InSARFlow
--------------------------------------

This file reads config file for processing interferograms in InSARFlow
using ISCE and time-series analysis using GIAnT.

Notes
-----
    Generally, all processing steps in InSARFlow should be done sequentially.
    Tasks completed can be set to false to skip running it again. 
    For example, after downloading SAR data, set DownloadImages = 'false' to save
    time if you want to re-processing any step.
    You can also download SAR from other sources, but the CSV files must include
    necessary information.
"""

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='InSARFlow parallel processing model')
    parser.add_argument('-c','--config', type=str, required=True, help='Config file for InSARFlow', dest='config')
    arg = parser.parse_args()
    
    return arg


def str2bool(inp):
    return inp.lower() in ("yes", "true", "1")


if __name__ == '__main__':    
    if len(sys.argv) != 3:
        print('Error: Number of arguments is not matched!')
        print('Run: $ InSARFlow.py -c config_filename')
        sys.exit()
    else:
        args = cmdLineParse()
        file_config = args.config
        
    # Read config file
    config = configparser.ConfigParser()
    config.read(file_config)
    fileASF = config['PROJECT']['ASF_File']    
    project_name = os.path.splitext(fileASF)[0]
    CreateParameters = str2bool(config['ISCE']['CreateParameters'])
    RunScript = str2bool(config['ISCE']['RunScript'])
    RunGIAnT = str2bool(config['GIANT']['RunGIAnT'])
    
    data = pd.read_csv(fileASF)
    platform=np.unique(data['Platform'])[0]
    pathnum=np.unique(data['Path Number'])[0]
    framenum = np.unique(data['Frame Number'])
    
    # Set up SAR matrix in pandas dataframe
    if platform == 'Sentinel-1A':
        sar = pd.DataFrame({pathnum:framenum})
        auxlink = config['PROJECT']['AuxilliaryLink']
    elif platform == 'ALOS':
        if np.isscalar(pathnum):
            sar = pd.DataFrame(np.vstack([framenum]).T, columns=[pathnum])
        else:
            sar = pd.DataFrame(np.vstack([framenum]*len(pathnum)).T, columns=pathnum)
    else:
        print('Error: Platform not recognized...')
        print('InSARFlow currently supports ALOS and Sentinel-1.')
        print('Exit!!!')
        sys.exit()

    """
    SET OPTIONS FOR RUNNING ISCE ...........................
    """        
    if platform == 'Sentinel-1A':
        Opts =  isfo.SEN1A_Options( 
                DownloadImages = str2bool(config['ISCE']['DownloadImages']),          # SLCs data will be download from ASF website
                SelectRegion = str2bool(config['ISCE']['SelectRegion']),              # Select specific region for processing                
                GenerateXML = str2bool(config['ISCE']['GenerateXML']),                # Create XML files for isce processing
                RunIFGs = str2bool(config['ISCE']['RunIFGs']),                        # Run ISCE for processing
                MPIMultipleNodes = str2bool(config['ISCE']['MPIMultipleNodes']),      # Run ISCE in parallel
                GenerateRoipac = str2bool(config['ISCE']['GenerateRoipac']),          # Create Roipac files for GIAnT runs
                CleanFiles = str2bool(config['ISCE']['CleanFiles']),                  # Remove all files that are not used in GIAnT (No need for SEN1A)
                TemporalBaselineThreshold = float(config['ISCE']['TemporalBaselineThreshold']),# Unit [day]
                OpenMP_Num_Threads = int(config['ISCE']['OpenMP_Num_Threads']),       # Number of threads used in OpenMP for ISCE.
                PrepareXML = str2bool(config['GIANT']['PrepareXML']),
                PrepareIgram = str2bool(config['GIANT']['PrepareIgram']),
                ProcessStack = str2bool(config['GIANT']['ProcessStack']),
                RunInversion = str2bool(config['GIANT']['RunInversion']),
                InvertMethod = config['GIANT']['InvertMethod'],
                )
        if Opts.SelectRegion:
            Opts.minLatitude = float(config['ISCE']['minimumLatitude'])
            Opts.maxLatitude = float(config['ISCE']['maximumLatitude'])
            Opts.minLongitude = float(config['ISCE']['minimumLongitude'])
            Opts.maxLongitude = float(config['ISCE']['maximumLongitude'])            

    elif platform == 'ALOS':
        Opts =  isfo.ALOS_Options( 
                Mode = config['ISCE']['Mode'],                                      # Processing mode, select 'insar' or 'stripmap'
                DownloadImages = str2bool(config['ISCE']['DownloadImages']),        # L1.0 data will be download from ASF website
                UnzipData = str2bool(config['ISCE']['UnzipData']),                  # data will be uncompressed
                BaselineCheck = str2bool(config['ISCE']['BaselineCheck']),          # a baseline check will be done to create pairs
                RemoveUnsedPairs = str2bool(config['ISCE']['RemoveUnsedPairs']),    # all non-satisfied pair folders will be remove.
                GenerateXML = str2bool(config['ISCE']['GenerateXML']),              # Generate xml files for each IFG folders for ISCE processing
                RunIFGs = str2bool(config['ISCE']['RunIFGs']),                      # Run ISCE for processing
                MPIMultipleNodes = str2bool(config['ISCE']['MPIMultipleNodes']),    # Run ISCE in parallel                
                GenerateRoipac = str2bool(config['ISCE']['GenerateRoipac']),        # Create Roipac files for GIAnT runs
                CleanFiles = str2bool(config['ISCE']['CleanFiles']),                # Remove all files that are not used in GIAnT
                TemporalBaselineThreshold = float(config['ISCE']['TemporalBaselineThreshold']),            # Unit [day]
                PerpendicularBaselineThreshold = float(config['ISCE']['PerpendicularBaselineThreshold']),  # Unit [m]
                OpenMP_Num_Threads = int(config['ISCE']['OpenMP_Num_Threads']),     # Number of threads used in OpenMP for ISCE.
                PrepareXML = str2bool(config['GIANT']['PrepareXML']),
                PrepareIgram = str2bool(config['GIANT']['PrepareIgram']),
                ProcessStack = str2bool(config['GIANT']['ProcessStack']),
                RunInversion = str2bool(config['GIANT']['RunInversion']),
                InvertMethod = config['GIANT']['InvertMethod'],
                )        
    

    """
    CREATE LIST OF FILES AND FOLDERS GENERATED DURING ISCE PROCESSING
    Users are recommended to use default names as shown below.
    """
    if platform == 'Sentinel-1A':
        listSAR =   isfo.SEN1A_Lists( 
                    Project = project_name,                                 # Folder name of the project
                    Platform = platform,                                    # Type of SAR data
                    LogFiles = config['ISCE']['LogFiles'],                  # Log file
                    AuxLink = auxlink,                                      # Link for downloading aux file
                    LogScreen = config['ISCE']['LogScreen'],                # Screen log of isce apps
                    DatePairList = config['ISCE']['DatePairList'],          # File includes pairs that are formed by BaselineCheck
                    ActiveList = config['ISCE']['ActiveList'],              # List of active (incomplete) pairs 
                    CompleteList = config['ISCE']['CompleteList'],          # List of complete pairs
                    BoundBox = config['ISCE']['BoundBox'],                  # Bounding Box of the region
                    IfgList = config['ISCE']['IfgList'],                    # Ifg list for GIANT
                    SubData = config['ISCE']['SubData'],                    # Subdata extracted from master CSV file
                    SLCDirectory = config['ISCE']['SLCDirectory'],          # Folder contains SLCs data
                    AuxDirectory = config['ISCE']['AuxDirectory'],          # Folder contains Auxliary data
                    PoeDirectory = config['ISCE']['PoeDirectory'],          # Folder contains POEORB data
                    ISCEDirectory = config['ISCE']['ISCEDirectory'],        # Folder for ISCE output processing
                    GIAnTDirectory = config['ISCE']['GIAnTDirectory'],      # Folder used for GIAnT processing
                    MISCDirectory = config['ISCE']['MISCDirectory'],        # Folder for Miscellaneous
                    )        
    
    elif platform == 'ALOS':
        listSAR =   isfo.ALOS_Lists(
                    Project = project_name,                                 # Folder name of the project
                    Platform = platform,                                    # Type of SAR data
                    LogFiles = config['ISCE']['LogFiles'],                  # Log file
                    dateID = config['ISCE']['dateID'],                      # File containing date info of ALOS images
                    LogScreen = config['ISCE']['LogScreen'],                # Screen log of isce apps
                    ALOSScenes = config['ISCE']['ALOSScenes'],              # File containing ALOS scene
                    DatePairList = config['ISCE']['DatePairList'],          # File includes pairs that are formed by BaselineCheck
                    ActiveList = config['ISCE']['ActiveList'],              # List of active (incomplete) pairs 
                    CompleteList = config['ISCE']['CompleteList'],          # List of complete pairs
                    BoundBox = config['ISCE']['BoundBox'],                  # Bounding Box of the region
                    IfgList = config['ISCE']['IfgList'],                    # Ifg list for GIANT
                    SubData = config['ISCE']['SubData'],                    # Subdata extracted from master CSV file
                    ZipDirectory = config['ISCE']['ZipDirectory'],          # Folder contains zip ALOS files
                    RawDirectory = config['ISCE']['RawDirectory'],          # Folder for ALOS raw extraction
                    ISCEDirectory = config['ISCE']['ISCEDirectory'],        # Folder for ISCE output processing
                    GIAnTDirectory = config['ISCE']['GIAnTDirectory'],      # Folder used for GIAnT processing
                    MISCDirectory = config['ISCE']['MISCDirectory'],        # Folder for Miscellaneous
                    )


    """
    CREATE CONFIG FILES AND RUN BASH SCRIPT
    """
    if platform == 'Sentinel-1A':
        # Create config files in each Path & Frame folder
        isfc.SEN1ACreateConfigs(data, Opts, CreateParameters, listSAR)

        # Run the bash script
        isfc.SEN1ARunISCEScripts(RunScript, listSAR)

    elif platform == 'ALOS':
        # Create config files in each Path & Frame folder
        isfc.ALOSCreateConfigs(data, sar, Opts, CreateParameters, listSAR)

        # Run the bash script
        isfc.ALOSRunISCEScripts(sar, RunScript, listSAR)


    """
    RUN GIAnT FOR TIME-SERIES ANALYSIS
    """
    if platform == 'Sentinel-1A':
        isfg.SEN1A_RunGIAnT(listSAR, Opts, platform, RunGIAnT)
    elif platform == 'ALOS':
        isfg.ALOS_RunGIAnT(sar, listSAR, Opts, platform, RunGIAnT)
