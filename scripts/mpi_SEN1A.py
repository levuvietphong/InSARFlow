#!/usr/bin/env python3

from mpi4py import MPI
import numpy as np
import pandas as pd
import os, sys, glob, re
import argparse
import subprocess
import timeit
import shutil

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Run insarApp.py in parallel using MPI4PY')
    parser.add_argument('-i','--input', type=str, required=True, help='List of insarApp.py files for each IFGs', dest='input')
    parser.add_argument('-d','--iscedir', type=str, required=True, help='isce product folder path', dest='iscedir')
    inputs = parser.parse_args()
    if (not inputs.input):
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


def delete_unused_files(scene):
    cwd = os.getcwd()
    os.chdir(scene.split()[0])
    files = ['isce.log','topsApp.xml','topsinsar.log','topsProc.xml']
    full_set = glob.glob('*') 
    del_set = list(filter(lambda x: x not in files, full_set))
    for file in del_set:
        try:
            os.remove(file)
        except:
            shutil.rmtree(file)
    print(scene.split()[0]+': cleaning completed!!!')
    os.chdir(cwd)


if __name__ == '__main__':
    '''
    Usage example
    srun -n #processors -d $ISCEdir -i $active_file
    '''
    inputs = cmdLineParse()
    insar_xml_list = inputs.input
    iscedir = inputs.iscedir
    full_list = GetFilePath(insar_xml_list)
    num_scenes = len(full_list)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    fout = open('mpi_logs.txt',"a")
    xml_files, col = DomainDecompose(comm,rank,size,insar_xml_list)
    filelog = ['screen.log','isce.log','topsApp.xml','topsinsar.log','topsProc.xml']
    filelist = ['topophase.cor.geo','filt_topophase.flat.geo', 'filt_topophase.unw.geo']
    dirlist = ['merged','master','slave','PICKLE']
    
    if rank==0:
        time_start=timeit.default_timer()
        fout.write(' SIMULATING %d PAIRS .............. \n' % num_scenes)
        fout.flush()        
    comm.Barrier()

    for j in range(0,col):
        tic=timeit.default_timer()
        cwd = os.getcwd()
        os.chdir(iscedir+'/'+xml_files[j][0])
        cmd = 'topsApp.py topsApp.xml --start="startup" >> screen.log'
        fout.write('CPU '+str(rank)+' running at ' + xml_files[j][0] + '\n')
        fout.flush()
        
        # First, run topsApp for processing
        subprocess.call(cmd, shell=True)

        # Second, check unwrapping and geocoding
        # If fail, run again with step='unwrap'
        flag_run = True
        for file in filelist:
            if not os.path.isfile('./merged/'+file):
                flag_run = False

        # If missing any file, re-run unwrapping and geocoding
        if flag_run == False:
            # Print message if geocode final products are not found in merged folder of each pair
            # Update demfile list and keep the demfile for running again.
            demfile = glob.glob('demLat*')
            fout.write(' ******* WARNING - CPU '+str(rank)+' at ' + xml_files[j][0] + ' IS NOT COMPLETED!!! \n')
            fout.flush()
        else:
            # Empty demfile, all DEM fill be deleted later.
            demfile = []

        # Next, clean up unused folders and files in GIANT            
        # ... Delete files, except those in filelog + demfile
        all_files = next(os.walk('.'))[2]
        del_files = list(filter(lambda x: x not in filelog+demfile, all_files))
        for file in del_files:
            os.remove(file)

        # ... Delete subfolders not in the dirlist
        subdirs=next(os.walk('.'))[1]
        del_dir = list(filter(lambda x: x not in dirlist, subdirs))
        for d in del_dir:
            shutil.rmtree(d)

        os.chdir(cwd)
        toc=timeit.default_timer()
        fout.write('CPU '+str(rank)+' at ' + xml_files[j][0] + ' COMPLETED:' + str((toc-tic)/60.) + ' (min) \n')

        fout.flush()

    comm.Barrier()

    if (rank==0) and (num_scenes>0):
        time_end=timeit.default_timer()
        fout.write('TOTAL PROCESSING TIME:' + str((time_end-time_start)/60.) + ' (min) \n')
        fout.write('AVERAGE:' + str((time_end-time_start)/60./num_scenes) + ' (min/pair) \n')
        fout.write('NUM_SCENE:' + str(num_scenes) + ' \n')
        fout.write('---------------------- COMPLETED --------------------------\n')
        fout.write('\n')

    fout.close()
    
