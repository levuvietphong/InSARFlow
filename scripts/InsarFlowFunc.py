import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
from string import whitespace
import h5py
import os,sys,shutil,subprocess,math,datetime
from datetime import date

"""
Functions for InsarFlow
This module provides functions in InsarFlow for running ISCE and GIAnT
Author: Phong Le
Last modified: July, 2019
"""

def AlosCreateConfigs(data, sar, opts, flag_create, lists):
    #####################################################################
    # This function create a config file for processing ALOS-PALSAR data
    #####################################################################
    flog = open(lists.LogFiles,"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('CREATING CONFIGS FILES FOR ALOS InSAR ...\n') 
    flog.flush()
    for path in sar.columns:
        frames = sar[path]
        for frame in frames:
            if ~np.isnan(frame):
                flog.write('PATH: '+str(path)+' AND FRAME: '+str(int(frame))+'\n'); flog.flush()
                directory = 'P'+str(path)+'_F'+str(int(frame))
                if not os.path.exists(directory):
                    os.makedirs(directory)
                
                sub_data = data[(data['Path Number'] == int(path)) & (data['Frame Number'].isin(frames))]
                sub_data.to_csv(directory+'/'+lists.SubData,index=False)

                if flag_create:
                    # Create parameters in bash file for ALOS
                    fout = open(directory+'/ALOS_parameters.cfg','w')
                    orbit = data[(data['Path Number']==int(path)) & (data['Frame Number']==int(frame))]['Orbit']
                    fout.write('sensor="ALOS" \n')
                    fout.write('processinglevel=L1.0 \n')
                    fout.write('parallel_scenes=4 \n')
                    fout.write('path='+str(path)+'\n')
                    fout.write('frame='+str(int(frame))+'\n')
                    orbitstring = str(orbit.values)
                    orbitstring = np.array2string(orbit.values, separator=',')
                    orbitstring = orbitstring.translate(dict.fromkeys(map(ord, whitespace)))
                    fout.write('abs_orbit='+orbitstring.strip('[]')+'\n \n')
                    
                    minLat = data[(data['Path Number']==int(path)) & (data['Frame Number']==int(frame))]['Near Start Lat'].min()
                    maxLat = data[(data['Path Number']==int(path)) & (data['Frame Number']==int(frame))]['Far End Lat'].min()
                    minLon = data[(data['Path Number']==int(path)) & (data['Frame Number']==int(frame))]['Near End Lon'].min()
                    maxLon = data[(data['Path Number']==int(path)) & (data['Frame Number']==int(frame))]['Far Start Lon'].max()

                    fout.write('minLat=%.3f           # minimum latitude \n' % minLat)
                    fout.write('maxLat=%.3f           # maximum latitude \n' % maxLat)
                    fout.write('minLon=%.3f           # minimum longitude \n' % minLon)
                    fout.write('maxLon=%.3f           # maximum longitude \n \n' % maxLon)

                    fout.write('minLat_int=%d           # minimum latitude (integer) \n' % np.floor(minLat))
                    fout.write('maxLat_int=%d           # maximum latitude (integer) \n' % math.ceil(maxLat))
                    fout.write('minLon_int=%d           # minimum longitude (integer) \n' % np.floor(minLon))
                    fout.write('maxLon_int=%d           # maximum longitude (integer) \n \n' % math.ceil(maxLon))

                    fout.write('pmode=%s \n' % opts.ProcessingMode)
                    fout.write('flag_download=%s \n' % opts.DownloadImages)
                    fout.write('flag_unzip=%s \n' % opts.UnzipData)
                    fout.write('flag_baseline=%s \n' % opts.BaselineCheck)
                    fout.write('flag_rup=%s \n' % opts.RemoveUnsedPairs)
                    fout.write('flag_insar=%s \n' % opts.GenerateXML)
                    fout.write('flag_ifgs=%s \n' % opts.RunIFGs)
                    fout.write('flag_rpac=%s \n' % opts.GenerateRoipac)
                    fout.write('flag_clean=%s \n' % opts.CleanFiles)
                    fout.write('perp_bsln=%d \n' % opts.PerpendicularBaselineThreshold)
                    fout.write('temp_bsln=%d \n' % opts.TemporalBaselineThreshold)
                    fout.write('omp_threads=%d \n' % opts.OpenMP_Num_Threads)

                    fout.write('zipdir=%s  \n' % lists.ZipDirectory)
                    fout.write('rawdir=%s  \n' % lists.RawDirectory)
                    fout.write('ISCEdir=%s  \n' % lists.ISCEDirectory)
                    fout.write('GIAnTdir=%s  \n' % lists.GIAnTDirectory)
                    fout.write('scriptdir=%s  \n' % os.path.dirname(__file__))
                    fout.write('dateID=%s  \n' % lists.dateID)
                    fout.write('screenlog=%s  \n' % lists.LogScreen)
                    fout.write('DatePairList=%s  \n' % lists.DatePairList)
                    fout.write('ActiveList=%s  \n' % lists.ActiveList)
                    fout.write('CompleteList=%s  \n' % lists.CompleteList)
                    fout.write('scenefile=%s  \n' % lists.ALOSScenes)
                    fout.write('bbox=%s  \n' % lists.BoundBox)
                    fout.write('ifglist=%s  \n' % lists.IfgList)
                    fout.write('asf_data_file=%s  \n' % lists.SubData)
                    fout.close()
    flog.close()


def Sen1ACreateConfigs(data, opts, flag_create, lists):
    #####################################################################
    # This function create a config file for processing SENTINEL-1A data
    #####################################################################
    flog = open(lists.Project+'/'+lists.LogFiles,"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('CREATING CONFIGS FILES FOR SENTINEL-1A InSAR ...\n') 
    flog.flush()

    pathscript = os.path.dirname(__file__)
    flog.write('RUNNING %s \n' % lists.Project)
    directory = lists.Project
    if not os.path.exists(directory):
        os.makedirs(directory)

    sub_data = data
    sub_data.to_csv(directory+'/'+lists.SubData,index=False)

    if flag_create:
        # Create parameters in bash file for ALOS
        fout = open(directory+'/SEN1A_parameter.cfg','w')
        fout.write('sensor="SENTINEL-1A" \n')
        fout.write('processinglevel=SLC \n')
        fout.write('auxlink=%s \n' % lists.AuxLink)
        fout.write('\n')
        
        if opts.SelectRegion == 'true':
            minLat = opts.minLatitude
            maxLat = opts.maxLatitude
            minLon = opts.minLongitude
            maxLon = opts.maxLongitude
        else:
            minLat = data['Near End Lat'].min()
            maxLat = data['Far Start Lat'].max()
            minLon = data['Far End Lon'].min()
            maxLon = data['Near Start Lon'].max()

        # Check if specified region is with images
        if opts.SelectRegion == 'true':
            if minLat < data['Near End Lat'].min():
                print('Error: Minimum latitude outside common region of SAR images. Exiting!!!')
                print('Minimum latitude of specified region: %f' % minLat)
                print('Common minimum latitude of SAR images: %f' % data['Near End Lat'].min())
                sys.exit()

            if maxLat > data['Far Start Lat'].max():
                print('Error: Maximum latitude outside common region of SAR images. Exiting!!!')
                print('Maximum latitude of specified region: %f' % maxLat)
                print('Common maximum Latitude of SAR images: %f' % data['Far Start Lat'].max())
                sys.exit()

            if minLon < data['Far End Lon'].min():
                print('Error: Minimum longitude outside common region of SAR images. Exiting!!!')
                print('Minimum longitude of specified region: %f' % minLon)
                print('Common minimum longitude of SAR images: %f' % data['Far End Lon'].min())
                sys.exit()

            if maxLon > data['Near Start Lon'].max():
                print('Error: Maximum longitude outside common region of SAR images. Exiting!!!')
                print('Maximum longitude of specified region: %f' % maxLon)
                print('Common maximum longitude of SAR images: %f' % data['Near Start Lon'].max())
                sys.exit()

        # Writing to config file
        fout.write('minLat=%.3f           # minimum latitude \n' % minLat)
        fout.write('maxLat=%.3f           # maximum latitude \n' % maxLat)
        fout.write('minLon=%.3f           # minimum longitude \n' % minLon)
        fout.write('maxLon=%.3f           # maximum longitude \n \n' % maxLon)

        fout.write('minLat_int=%d           # minimum latitude (integer) \n' % np.floor(minLat))
        fout.write('maxLat_int=%d           # maximum latitude (integer) \n' % math.ceil(maxLat))
        fout.write('minLon_int=%d           # minimum longitude (integer) \n' % np.floor(minLon))
        fout.write('maxLon_int=%d           # maximum longitude (integer) \n \n' % math.ceil(maxLon))

        fout.write('flag_download=%s \n' % opts.DownloadImages)
        fout.write('flag_topsar=%s \n' % opts.GenerateXML)
        fout.write('flag_ifgs=%s \n' % opts.RunIFGs)
        fout.write('flag_rpac=%s \n' % opts.GenerateRoipac)
        fout.write('flag_clean=%s \n' % opts.CleanFiles)
        fout.write('temp_bsln=%d \n' % opts.TemporalBaselineThreshold)
        fout.write('omp_threads=%d \n' % opts.OpenMP_Num_Threads)

        fout.write('pathscript=%s  \n' % pathscript)
        fout.write('slcdir=%s  \n' % lists.SLCDirectory)
        fout.write('auxdir=%s  \n' % lists.AuxDirectory)
        fout.write('poedir=%s  \n' % lists.PoeDirectory)
        fout.write('ISCEdir=%s  \n' % lists.ISCEDirectory)
        fout.write('GIAnTdir=%s  \n' % lists.GIAnTDirectory)
        
        fout.write('scriptdir=%s  \n' % os.path.dirname(__file__))
        fout.write('screenlog=%s  \n' % lists.LogScreen)
        fout.write('DatePairList=%s  \n' % lists.DatePairList)
        fout.write('ActiveList=%s  \n' % lists.ActiveList)
        fout.write('CompleteList=%s  \n' % lists.CompleteList)
        fout.write('bbox=%s  \n' % lists.BoundBox)
        fout.write('ifglist=%s  \n' % lists.IfgList)
        fout.write('asf_data_file=%s  \n' % lists.SubData)
        fout.close()
    flog.close()


def AlosRunISCEScripts(sar, flag_run, lists):
    #####################################################################
    # This function implement the run_scripts_ALOS.sh in bash shell
    # Note: The run is outside python env
    #####################################################################
    flog = open(lists.LogFiles,"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('PROCESSING ISCE FOR ALOS InSAR ...\n') 
    flog.flush()
    
    pathscript = os.path.dirname(__file__)
    for path in sar.columns:
        frames = sar[path]
        for frame in frames:
            if ~np.isnan(frame):
                flog.write('PATH: '+str(path)+' AND FRAME: '+str(int(frame))+'\n'); flog.flush()
                directory = 'P'+str(path)+'_F'+str(int(frame))
                if not os.path.exists(directory):
                    print('Error: Folder %s is not existed!' % directory)
                else:
                    if flag_run:
                        cwd = os.getcwd()
                        os.chdir(directory)
                        cmd = "sh " + pathscript + "/run_scripts_ALOS.sh"
                        subprocess.call(cmd, shell=True)
                        os.chdir(cwd)
    flog.close()


def Sen1ARunISCEScripts(flag_run, lists):
    #####################################################################
    # This function implement the run_scripts_SEN1A.sh in bash shell
    # Note: The run is outside python env
    #####################################################################
    flog = open(lists.Project+'/'+lists.LogFiles,"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('PROCESSING ISCE FOR SENTINEL-1A InSAR ...\n') 
    flog.flush()
    
    pathscript = os.path.dirname(__file__)
    flog.write('RUNNING %s \n' % lists.Project)
    directory = lists.Project
    if not os.path.exists(directory):
        print('Error: Folder %s is not existed!' % directory)
    else:
        if flag_run:
            cwd = os.getcwd()
            os.chdir(directory)
            cmd = "sh " + pathscript + "/run_scripts_SEN1A.sh"
            subprocess.call(cmd, shell=True)
            os.chdir(cwd)
    flog.close()


def RunGIAnTScripts(project, platform, sar, prep, igram, processtack, invert, gmode):
    #####################################################################
    # This function calls GIAnT processing scripts for time-series analysis
    #####################################################################    
    flog = open('log_giant.txt',"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('RUNNING GIANT FOR TIME SERIES ANALYSIS ...\n') 
    flog.flush()

    pathscript = os.path.dirname(os.path.dirname(__file__))
    if platform == 'ALOS':
        for path in sar.columns:
            frames = sar[path]
            for frame in frames:
                if ~np.isnan(frame):
                    flog.write('PATH: '+str(path)+' AND FRAME: '+str(int(frame))+'\n'); flog.flush()
                    directory = 'P'+str(path)+'_F'+str(int(frame))+'/GIAnT'
                    if not os.path.exists(directory):
                        flog.write('Error: GIAnT folder does NOT exist \n')
                        flog.flush()
                        exit()
                    
                    cwd = os.getcwd()
                    os.chdir(directory)
                    fout = open('output.txt',"a")            
                    if prep:                
                        fout.write('Running ./prepxml_SBAS_ALOS.py \n')
                        subprocess.call("./prepxml_SBAS_ALOS.py", shell=True)
                    if igram:
                        fout.write('Running PrepIgramStack.py \n')
                        subprocess.call("PrepIgramStack.py >> output.txt", shell=True)
                    if processtack:
                        fout.write('Running ProcessStack.py \n')
                        subprocess.call("ProcessStack.py >> output.txt", shell=True)
                    if invert:
                        if gmode == 'sbas':
                            fout.write('Running SBASInvert.py \n')
                            subprocess.call("SBASInvert.py >> output.txt", shell=True)
                            subprocess.call("SBASxval.py >> output.txt", shell=True)
                        else:
                            fout.write('Running NSBASInvert.py \n')
                            subprocess.call("NSBASInvert.py >> output.txt", shell=True)
                            subprocess.call("NSBASxval.py >> output.txt", shell=True)
                    fout.close()
                    os.chdir(cwd)

    if platform == 'Sentinel-1A':
        print('Platform: %s' % platform)
        directory = project+'/GIAnT'
        if not os.path.exists(directory):
            flog.write('Error: GIAnT folder does NOT exist \n')
            flog.flush()
            exit()
        
        cwd = os.getcwd()
        os.chdir(directory)
        fout = open('output.txt',"a")            
        if prep:                
            fout.write('Running ./prepxml_SBAS_SEN1A.py \n')
            subprocess.call("./prepxml_SBAS_SEN1A.py", shell=True)
        if igram:
            fout.write('Running PrepIgramStack.py \n')
            subprocess.call("PrepIgramStack.py >> output.txt", shell=True)
        if processtack:
            fout.write('Running ProcessStack.py \n')
            subprocess.call("ProcessStack.py >> output.txt", shell=True)
        if invert:
            if gmode == 'sbas':
                fout.write('Running SBASInvert.py \n')
                subprocess.call("SBASInvert.py >> output.txt", shell=True)
                subprocess.call("SBASxval.py >> output.txt", shell=True)
            else: #nsbas
                fout.write('Running NSBASInvert.py \n')
                subprocess.call("NSBASInvert.py >> output.txt", shell=True)
                #subprocess.call("NSBASxval.py >> output.txt", shell=True)
        fout.close()
        os.chdir(cwd)

    flog.close()


def ConvertToTiffFiles(sar):
    flog = open('log_GIS.txt',"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('CONVERTING TO TIFF FORMAT ...\n') 
    flog.flush()