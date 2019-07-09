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
    parser.add_argument('-o','--output', type=str, required=True, help='Output list of incompleted ifgs ', dest='output')
    inputs = parser.parse_args()    
    return inputs


def delete_unused_files(scene):
    cwd = os.getcwd()
    os.chdir(scene.split()[0])
    log_set = ['geo.log', 'insarApp.xml', 'insar.log', 'insarProc.xml', 'isce.log', 'screen_geocode.log', 'screen.log']
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
    if len(sys.argv) == 1:
        print('Sen1A_check_ifgs_files.py -l list')
        sys.exit()
    else:
        inputs = cmdLineParse()
        iscedir = inputs.isce
        active_list = inputs.list
        out_list = inputs.output
    
    # List of files will be checked
    filelist = ['filt_topophase.flat.geo', 'filt_topophase.unw.conncomp.geo', 'filt_topophase.unw.geo', 'phsig.cor.geo']
    
    # Create a file checking active pairs
    fout= open(out_list,"w")

    # Remove unnecessary files in each pairs
    pairs = open(active_list)
    incomplete_pairs = 0
    num_pairs = 0
    for line in pairs:
        pairdir = line.split('\n')[0]
        flag_run = True
        scene = iscedir + '/' + pairdir + '/merged'
        cwd = os.getcwd()
        os.chdir(scene)
        for file in filelist:
            if not os.path.isfile(file):
                flag_run = False

        # If missing any file, set flag_run to False and update pairdir to active pair file
        if flag_run == False:
            incomplete_pairs += 1                
            fout.write('%s \n' % pairdir)
        
        num_pairs += 1
        os.chdir(cwd)
    
    print('- NUMBER OF PAIRS FAILED: %d \n' % incomplete_pairs)
    print('- NUMBER OF PAIR COMPLETED: %d \n' % (num_pairs-incomplete_pairs))
    
    # Close active pair file
    print('Incomplete pair file (%s) has been created \n' % out_list)
    print('See list of pairs will be unwrapped and geocoded in %s \n' % out_list)
    fout.close()