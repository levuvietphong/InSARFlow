import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import os,sys,shutil,subprocess,math,datetime
from datetime import date


def ALOS_RunGIAnT(sar, lists, opts, platform, run):
    #####################################################################
    # This function implements set of functions to perform GIAnT for ALOS output
    #####################################################################
    flog = open(lists.Project+'/log_giant.txt',"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('RUNNING GIAnT FOR ALOS ...\n') 
    flog.flush()
    
    pathscript = os.path.dirname(__file__)
    for path in sar.columns:
        frames = sar[path]
        for frame in frames:
            if ~np.isnan(frame):
                flog.write('PATH: '+str(path)+' AND FRAME: '+str(int(frame))+'\n'); flog.flush()
                print('PATH: '+str(path)+' AND FRAME: '+str(int(frame)))
                directory = lists.Project+'/P'+str(path)+'_F'+str(int(frame))+'/'+lists.GIAnTDirectory
                
                if not os.path.exists(directory):
                    print('Error: Folder %s is not existed!' % directory)
                else:
                    if run:
                        cwd = os.getcwd()
                        os.chdir(directory)
                        config = 'ALOS_parameters.cfg'
                        if opts.MPIMultipleNodes:
                            cmd = "sbatch %s/qsub_GIAnT.sh %s %s %s" % (pathscript, pathscript, config, platform)
                        else:
                            cmd = "/%s/run_GIAnT.sh %s %s" % (pathscript, config, platform)
                        
                        subprocess.call(cmd, shell=True)            
                        os.chdir(cwd)
    flog.close()


def SEN1A_RunGIAnT(lists, opts, platform, run):
    #####################################################################
    # This function implements set of functions to perform GIAnT for SEN1A output
    #####################################################################
    flog = open(lists.Project+'/log_giant.txt',"a")
    flog.write('---------------------------------------------------\n')
    flog.write('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    flog.write('RUNNING GIAnT FOR SENTINEL-1A InSAR ...\n') 
    print('---------------------------------------------------\n')
    print('TIME: %s \n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    print('RUNNING GIAnT FOR SENTINEL-1A InSAR ...\n') 
    flog.flush()
    
    pathscript = os.path.dirname(__file__)
    directory = lists.Project+'/'+lists.GIAnTDirectory
    flog.write('PROJECT: %s \n' % directory)
    print('PROJECT: %s \n' % directory)
    
    if not os.path.exists(directory):
        print('Error: Folder %s is not existed!' % directory)
    else:
        if run:
            cwd = os.getcwd()
            os.chdir(directory)
            config = 'SEN1A_parameters.cfg' 
            if opts.MPIMultipleNodes:
                cmd = "sbatch %s/qsub_GIAnT.sh %s %s %s" % (pathscript, pathscript, config, platform)
            else:
                cmd = "/%s/run_GIAnT.sh %s %s" % (pathscript, config, platform)

            subprocess.call(cmd, shell=True)            
            os.chdir(cwd)
    flog.close()