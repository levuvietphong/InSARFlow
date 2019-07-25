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
    parser.add_argument('-i','--iscedir', type=str, required=False, help='ISCE folder path', dest='isce')
    parser.add_argument('-l','--list', type=str, required=True, help='List of folders containing pairs', dest='list')
    inputs = parser.parse_args()    
    return inputs


if __name__ == '__main__':
    if len(sys.argv) !=5:
        print('Check_Interferogram_SEN1A_nowrite.py -i iscedir -l list')
        sys.exit()
    else:
        inputs = cmdLineParse()
        iscedir = inputs.isce
        isce_xml_list = inputs.list
    
    filelist = ['isce.log', 'topsApp.xml', 'topsinsar.log', 'topsProc.xml']
    dirlist = ['merged']
    pairs = open(isce_xml_list)

    active_pairs = 0
    num_pairs = 0
    for line in pairs:
        pairdir = line.split('\n')[0]
        flag_run = True
        scene = iscedir + '/' + pairdir
        cwd = os.getcwd()
        os.chdir(scene)
        filt_set = glob.glob(dirlist[0]+'/filt_topophase.unw*')
        cor_set = glob.glob(dirlist[0]+'/topophase.cor*') 
        for file in filelist:
            if not os.path.isfile(file):
                flag_run = False

        if len(filt_set) < 8:
            flag_run = False
        
        if len(cor_set) < 4:
            flag_run = False

        # If missing any file, set flag_run to False and update pairdir to active pair file
        if flag_run == False:
            active_pairs += 1                

        num_pairs += 1
        os.chdir(cwd)
    
    print('- NUMBER OF PAIRS WILL BE PROCESSED: %d \n' % active_pairs)
    print('- NUMBER OF PAIR COMPLETED: %d \n' % (num_pairs-active_pairs))