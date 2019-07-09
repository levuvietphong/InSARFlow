#!/usr/bin/env python

import os, sys, glob, re
import argparse
import datetime
import numpy as np
import pandas as pd
import shutil


def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Checking IFGs files before running')
    parser.add_argument('-m','--mode', type=str, required=True, help='mode for processing', dest='mode')    
    parser.add_argument('-i','--iscedir', type=str, required=False, help='ISCE folder path', dest='isce')
    parser.add_argument('-l','--list', type=str, required=True, help='List of folders containing pairs', dest='list')
    parser.add_argument('-a','--active', type=str, required=True, help='Output list of active incompleted ifgs ', dest='active')
    parser.add_argument('-c','--complete', type=str, required=True, help='Output list of completed ifgs ', dest='complete')
    inputs = parser.parse_args()    
    return inputs


if __name__ == '__main__':
    if len(sys.argv) < 7:
        print('Check_Interferogram_ALOS.py.py -l list -a active -c complete')
        sys.exit()
    else:
        inputs = cmdLineParse()
        pmode = inputs.mode
        iscedir = inputs.isce
        isce_xml_list = inputs.list
        active_list = inputs.active
        complete_list = inputs.complete
        
    # Create a file checking active pairs
    fact= open(active_list,"w")
    fcom= open(complete_list,"w")

    # Remove unnecessary files in each pairs
    pairs = open(isce_xml_list)
    active_pairs = 0
    num_pairs = 0
    for line in pairs:
        pairdir = line.split('\n')[0]
        flag_run = True
        scene = iscedir + '/' + pairdir
        cwd = os.getcwd()
        os.chdir(scene)
        if pmode=='insar':
            filelist = ['isce.log', 'insarApp.xml', 'insarProc.xml']
            filt_set = glob.glob('filt_topophase.unw.geo*')
            cor_set = glob.glob('topophase.cor.geo*')             
        elif pmode=='stripmap':
            filelist = ['isce.log', 'stripmapApp.xml', 'stripmapProc.xml']
            filt_set = glob.glob('interferogram/filt_topophase.unw.geo*')
            cor_set = glob.glob('interferogram/topophase.cor.geo*')             

        # Check if list of files and folders exist
        for file in filelist:
            if not os.path.isfile(file):
                flag_run = False

        if len(filt_set) < 3:
            flag_run = False
        
        if len(cor_set) < 3:
            flag_run = False

        # If missing any file, set flag_run to False and update pairdir to active pair file
        if flag_run == False:
            #print('Processing pair %s for topsApp.\n' % pairdir)
            active_pairs += 1                
            fact.write('%s \n' % pairdir)
        else:
            fcom.write('%s \n' % pairdir)

        num_pairs += 1
        os.chdir(cwd)
    
    fact.close()
    fcom.close()

    print('- TOTAL NUMBER OF PAIRS: %d \n' % num_pairs)
    print('- NUMBER OF PAIRS WILL BE PROCESSED: %d \n' % active_pairs)
    print('- NUMBER OF PAIR COMPLETED: %d \n' % (num_pairs-active_pairs))
    print('Complete pair file (%s) has been created \n' % complete_list)
    print('Active pair file (%s) has been created \n' % active_list)
    print('See list of pairs will be processed in %s \n' % active_list)
