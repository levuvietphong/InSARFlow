#!/usr/bin/env python3

import os, sys, glob, re
import argparse
import numpy as np
import pandas as pd
import shutil

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Remove pairs that do not meet baseline conditions')
    parser.add_argument('-i','--isce', type=str, required=True, help='SAR directory for processing', dest='isce')    
    parser.add_argument('-s','--scenes', type=str, required=True, help='list of scenes used', dest='scenes')
    parser.add_argument('-p','--pairs', type=str, required=True, help='list of pairs selected', dest='pairs')    
    arg = parser.parse_args()
    
    return arg


def clean_scenes_pairs(dir,scene,pair):
    f = open(scene)
    scene_dirs = []
    for line in f:
        scene = line.split('\n')[0]
        scene_dirs.append('./'+dir+'/'+scene)
    f.close()

    f = open(pair)
    pair_dirs = []
    for line in f:
        pairs = line.split('\n')[0]
        dates = re.findall(r"[-+]?\d*\.\d+|\d+", pairs)
        pair_dirs.append('./'+dir+'/'+dates[0]+'__'+dates[1])
    f.close()

    all_dirs=[]
    for root, dirs, files in os.walk('./'+dir):
        all_dirs.append(root)
            
    rem_dirs = [s for s in all_dirs if s not in pair_dirs+scene_dirs+['./'+dir]+['./'+dir+'/PICKLE']]
    for d in rem_dirs:
        if os.path.exists(d):
            shutil.rmtree(d)

if __name__ == '__main__':    
    if len(sys.argv) != 7:
        print('Clean_Unused_Pairs_ALOS.py -d directory -p pairs')
        sys.exit()
    else:
        args = cmdLineParse()
        iscedir = args.isce
        scenefiles = args.scenes
        pairfiles = args.pairs
        
    clean_scenes_pairs(iscedir, scenefiles, pairfiles)
