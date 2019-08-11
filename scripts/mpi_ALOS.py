#!/usr/bin/env python3

from mpi4py import MPI
import numpy as np
import pandas as pd
import os, sys, glob, re
import argparse
import subprocess
import timeit
import CleanALOS

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Run insarApp.py in parallel using MPI4PY')
    parser.add_argument('-m','--mode', type=str, required=True, help='mode for processing', dest='mode')
    parser.add_argument('-r','--rawdir', type=str, required=True, help='raw data folder root path', dest='raw')
    parser.add_argument('-l','--list', type=str, required=True, help='List of insarApp.py files for each IFGs', dest='list')
    parser.add_argument('-d','--iscedir', type=str, required=True, help='insar folder path', dest='isce')
    inputs = parser.parse_args()
    if (not inputs.list):
        print('Error!!! No input list is provided.')
        sys.exit(0)    
    
    return inputs


def GetFilePath(filelist):
    full_list = []
    file = open(filelist)
    for line in file:
        scene = line.split('\n')[0]
        full_list.append(scene.split())
    return full_list


def DomainDecompose(comm,rank,size,input):
    
    file_list = GetFilePath(input)
    if np.shape(file_list)[0] == 0:
        sys.exit(0)

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
    '''
    Usage example
    mpirun -n #processors -i xml_input
    '''
    inputs = cmdLineParse()
    pmode = inputs.mode
    rawdir = inputs.raw
    iscedir = inputs.isce
    isce_xml_list = inputs.list
    full_list = GetFilePath(isce_xml_list)
    num_scenes = len(full_list)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    fout = open('mpi_ALOS_logs.txt',"a")
    xml_files, col = DomainDecompose(comm,rank,size,isce_xml_list)

    if rank==0:
        time_start=timeit.default_timer()
    comm.Barrier()

    if pmode=='insar':
        runisce = 'insarApp.py insarApp.xml'
    elif pmode=='stripmap':
        runisce = 'stripmapApp.py stripmapApp.xml'

    for j in range(0,col):
        tic=timeit.default_timer()
        cwd = os.getcwd()
        os.chdir(iscedir+'/'+xml_files[j][0])
        cmd = runisce + ' --start="startup" >> screen.log'
        fout.write('CPU '+str(rank)+' running at ' + xml_files[j][0] + '\n')
        fout.flush()
        
        # Run ISCE app
        subprocess.call(cmd, shell=True)
        CleanALOS.LargeFolders(pmode)

        os.chdir(cwd)
        toc=timeit.default_timer()
        fout.write('CPU '+str(rank)+' at ' + xml_files[j][0] + ' COMPLETED:' + str((toc-tic)/60.) + ' (min) \n')
        fout.flush()

    comm.Barrier()

    if (rank==0) and (num_scenes>0):
        time_end=timeit.default_timer()
        fout.write('TOTAL PROCESSING TIME:' + str((time_end-time_start)/60.) + ' (min) \n')
        fout.write('AVERAGE:' + str((time_end-time_start)/60./num_scenes) + ' (min/pair) \n')
        fout.write('NUMBER OF SCENES:' + str(num_scenes) + ' \n')
        fout.write('---------------------- COMPLETED --------------------------\n')
        fout.write('\n')

    fout.close()
    
