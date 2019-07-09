#!/usr/bin/env python

import os, sys, glob, re
import argparse
import datetime
import numpy as np
import pandas as pd
import shutil
import CleanALOS


def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Removing IFGs files unused.s')
    parser.add_argument('-m','--mode', type=str, required=True, help='mode for processing', dest='mode')    
    parser.add_argument('-r','--rawdir', type=str, required=True, help='raw data folder root path', dest='raw')
    parser.add_argument('-c','--dateIDfile', type=str, required=True, help='file to convert fileID to dates', dest='dates')    
    parser.add_argument('-i','--iscedir', type=str, required=True, help='isce folder path', dest='isce')
    parser.add_argument('-l','--list', type=str, required=True, help='List of date pairs', dest='list')
    inputs = parser.parse_args()    
    return inputs

def GetDateID(data_root, datefile):
    date_list = []
    datefile_full = data_root + '/' + datefile
    file = open(datefile_full)
    for line in file:
        date = line.split('\n')[0]
        date_list.append(date.split())
    return date_list


if __name__ == '__main__':
    inputs = cmdLineParse()
    pmode = inputs.mode
    raw_root = inputs.raw
    datefile = inputs.dates
    isce_dir = inputs.isce
    isce_xml_list = inputs.list
    
    # Remove unnecessary files in each pairs
    file = open(isce_xml_list)
    df = pd.DataFrame()
    for line in file:
        scene = line.split('\n')[0]
        cwd = os.getcwd()
        os.chdir(isce_dir+'/'+scene.split()[0])
        CleanALOS.AllFilesFolders(pmode)
        os.chdir(cwd)

    # Remove raw files of each scene in isce
    date_list = GetDateID(raw_root, datefile)
    for i, v in enumerate(date_list):
        remdir = isce_dir+'/'+v[1]
        try:
            shutil.rmtree(remdir)
        except:
            print(remdir+': has been removed already!!!')

    # Remove raw files in ALOW_raw
    for i, v in enumerate(date_list):
        remdir = raw_root+'/'+v[1]
        try:
            shutil.rmtree(remdir)
        except:
            print(remdir+': has been removed already!!!')