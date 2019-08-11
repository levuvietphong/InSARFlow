#!/usr/bin/env python3

from mpi4py import MPI
import numpy as np
import pandas as pd
import os, sys, glob, re
import argparse
import subprocess
import timeit

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Run insarApp.py in parallel using MPI4PY')
    parser.add_argument('-m','--mode', type=str, required=True, help='mode for processing', dest='mode')
    parser.add_argument('-i','--iscedir', type=str, required=False, help='ISCE folder path', dest='isce')
    parser.add_argument('-l','--list', type=str, required=True, help='List of folders containing *Proc.xml files', dest='list')
    parser.add_argument('-g','--gdir', type=str, required=True, help='GIAnT directory', dest='gdir')    
    inputs = parser.parse_args()    
    return inputs


def GetFilePath(filelist):
    full_list = []
    file = open(filelist)
    for line in file:
        scene = line.split('\n')[0]
        full_list.append(scene.split())
    return full_list

def cropping_dem(GIAnT,insardir):
    cwd = os.getcwd()
    os.chdir(insardir)
    cmd = "cp demfloat32* " + cwd +"/"+ GIAnT
    subprocess.call("imageMath.py -e a --a dem.crop -s BIL -t float32 -o demfloat32.crop", shell=True)
    print(cmd)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)

def DomainDecompose(comm,rank,size,input):
    
    file_list = GetFilePath(input)
    if rank == 0:
        numpairs = np.shape(file_list)[0]
        counts = np.arange(size,dtype=np.int32)
        displs = np.arange(size,dtype=np.int32)
        ave = int(numpairs / size)
        extra = numpairs % size
        offset = 0

        for i in range(0,size):
            col = ave if i<size-extra else ave+1
            counts[i] = col

            if i==0:
                col0 = col
                offset += col
                displs[i] = 0
            else:
                comm.send(offset, dest=i)
                comm.send(col, dest=i)
                offset += col
                displs[i] = displs[i-1] + counts[i-1]

        offset = 0
        col = col0

    comm.Barrier()

    if rank != 0: # workers
        offset = comm.recv(source=0)
        col = comm.recv(source=0)

    comm.Barrier()
    xml_files = file_list[offset:offset+col]
    return xml_files, col



if __name__ == '__main__':
    inputs = cmdLineParse()
    pmode = inputs.mode
    iscedir = inputs.isce
    insar_xml_list = inputs.list
    giant_dir = inputs.gdir
    full_list = GetFilePath(insar_xml_list)
    num_scenes = len(full_list)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    fout = open('mpi_geocode_log.txt',"a")
    xml_files, col = DomainDecompose(comm,rank,size,insar_xml_list)

    if rank==0:
        time_start=timeit.default_timer()
    comm.Barrier()

    if pmode=='insar':
        geoisce = 'insarApp.py insarApp.xml'
    elif pmode=='stripmap':
        geoisce = 'stripmapApp.py stripmapApp.xml'

    for j in range(0,col):
        tic=timeit.default_timer()
        cwd = os.getcwd()
        os.chdir(iscedir+'/'+xml_files[j][0])
        cmd = geoisce + ' --start="geocode"  >> screen_geocode.log'
        fout.write('CPU '+str(rank)+' running at ' + xml_files[j][0] + '\n')
        fout.flush()

        # Run ISCE app for geocode
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)
        toc=timeit.default_timer()
        fout.write('CPU '+str(rank)+' at ' + xml_files[j][0] + ' COMPLETED:' + str((toc-tic)/60.) + ' (min) \n')
        fout.flush()

    comm.Barrier()

    if rank==0:
        cropping_dem(giant_dir,iscedir+'/'+xml_files[0][0])    
        fout.write('Cropping DEMFLOAT32 \n')

        time_end=timeit.default_timer()
        fout.write('TOTAL PROCESSING TIME:' + str((time_end-time_start)/60.) + ' (min) \n')
        fout.write('AVERAGE:' + str((time_end-time_start)/60./num_scenes) + ' (min/pair) \n')
        fout.write('---------------------- COMPLETED --------------------------\n')
        fout.write('\n')
        
    fout.close()    
