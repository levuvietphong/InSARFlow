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
    parser = argparse.ArgumentParser(description='Removing IFGs files unused.s')
    parser.add_argument('-r','--rawdir', type=str, required=False, help='raw data folder root path', dest='raw')
    parser.add_argument('-c','--dateIDfile', type=str, default='dateID.info', help='file to convert fileID to dates', dest='dates')    
    parser.add_argument('-p','--insardir', type=str, required=False, help='insar folder path', dest='insar')
    parser.add_argument('-l','--list', type=str, required=True, help='List of folders containing insarProc.xml files', dest='list')
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


def delete_unused_files(scene):
    cwd = os.getcwd()
    os.chdir(scene.split()[0])
    log_set = ['geo.log','insarApp.xml','insar.log','insarProc.xml','isce.log','screen_geocode.log','screen.log']
    filt_set = glob.glob('filt_topophase.unw*')
    cor_set = glob.glob('topophase.cor*') 
    full_set = glob.glob('*') 
    del_set = list(filter(lambda x: x not in log_set+filt_set+cor_set, full_set))
    for file in del_set:
        try:
            os.remove(file)
        except:
            shutil.rmtree(file)
    print(scene.split()[0]+': cleaning completed!!!')
    os.chdir(cwd)


if __name__ == '__main__':
    if len(sys.argv) != 9:
        print('Sen1A_clean_ifgs_files.py -r rawdir -c dateIdFile -p insardir -l list')
        sys.exit()
    else:
        inputs = cmdLineParse()
        raw_root = inputs.raw
        datefile = inputs.dates
        insar_dir = inputs.insar
        insar_xml_list = inputs.list
    
    # Remove unnecessary files in each pairs
    file = open(insar_xml_list)
    df = pd.DataFrame()
    for line in file:
        scene = line.split('\n')[0]
        delete_unused_files(scene)

    # Remove raw files of each scene in INSAR
    date_list = GetDateID(raw_root, datefile)
    for i, v in enumerate(date_list):
        remdir = insar_dir+'/'+v[1]
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