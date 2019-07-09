#!/usr/bin/env python

import os, sys, glob, re
import datetime
import numpy as np
import pandas as pd
import shutil


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


def LargeFolders(pmode):
    cwd = os.getcwd()
    if pmode=='stripmap':
        remdir = ['SplitSpectrum', 'coregisteredSlc', 'denseOffsets', 'geometry', 'offsets', 'ionosphere']    
        for dir in remdir:
            if os.path.exists(dir):
                shutil.rmtree(dir)
                
        print(os.path.basename(cwd)+': Large folder cleaning is completed!!!')


def AllFilesFolders(pmode):
    cwd = os.getcwd()
    if pmode=='stripmap':   # Stripmap mode
        # Delete unused files in 'interferogram' folder
        if os.path.exists('./interferogram'):
            os.chdir('./interferogram')
            keep_set = glob.glob('filt_topophase.unw*')
            keep_set.extend(glob.glob('topophase.cor*'))
            keep_set.extend(glob.glob('phsig.cor*'))
            full_set = glob.glob('*') 
            del_set = list(filter(lambda x: x not in keep_set, full_set))
            extra_set = glob.glob('topophase.cor.full*')
            del_set = del_set + extra_set
            for file in del_set:
                try:
                    os.remove(file)
                except:
                    shutil.rmtree(file)
            os.chdir(cwd)

        # Delete unused files and folders in parent dir
        log_set = ['PICKLE', 'interferogram', 'stripmapApp.xml', 'stripmapProc.xml', 'insar.log', 'isce.log', 'screen.log']    
        keep_set = glob.glob('dem.crop*')
        full_set = glob.glob('*') 
        del_set = list(filter(lambda x: x not in log_set+keep_set, full_set))
        for file in del_set:
            try:
                os.remove(file)
            except:
                shutil.rmtree(file)
        print(os.path.basename(cwd)+': Cleaning is completed!!!')
    elif pmode=='insar':    # Insar mode
        # Delete unused files and folders in parent dir
        log_set = ['PICKLE', 'insarApp.xml', 'insarProc.xml', 'insar.log', 'isce.log', 'screen.log']    
        keep_set = glob.glob('filt_topophase.unw*')
        keep_set.extend(glob.glob('topophase.cor*'))
        keep_set.extend(glob.glob('phsig.cor*'))
        keep_set.extend(glob.glob('los.rdr*'))
        keep_set.extend(glob.glob('dem.crop*'))
        full_set = glob.glob('*') 
        del_set = list(filter(lambda x: x not in log_set+keep_set, full_set))
        for file in del_set:
            try:
                os.remove(file)
            except:
                shutil.rmtree(file)
        print(os.path.basename(os.getcwd())+': Cleaning is completed!!!')