#!/usr/bin/env python3

from mpi4py import MPI
import numpy as np
import argparse, subprocess
import os, sys, glob, re
import timeit
import shutil


def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Run insarApp.py in parallel using MPI4PY')
    parser.add_argument('-i','--input', type=str, required=True, help='run files', dest='input')
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
        full_list.append(scene)
    return full_list



def DomainDecompose(comm,rank,size,input):   
    file_list = GetFilePath(input)
    if rank == 0:
        numruns = np.shape(file_list)[0]
        counts = np.arange(size,dtype=np.int32)
        displs = np.arange(size,dtype=np.int32)
        ave = int(numruns / size)
        extra = numruns % size
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
    run_files = file_list[offset:offset+col]
    return run_files, col




if __name__ == '__main__':
    '''
    Usage example
    srun -n #processors -d $ISCEdir -i $active_file
    '''
    inputs = cmdLineParse()
    run_list = inputs.input
    process_list = GetFilePath(run_list)
    num_processes = len(process_list)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    fout = open('logs_' + run_list + '.txt',"a")
    
    if rank==0:
        time_start=timeit.default_timer()
        fout.write(' RUNNING %d PROCESSES .............. \n' % num_processes)
        fout.flush()        
    comm.Barrier()

    run_files, col = DomainDecompose(comm,rank,size,run_list)
    for j in range(0,col):
        tc_start = timeit.default_timer()
        subprocess.call(run_files[j], shell=True)
        tc_end = timeit.default_timer()
        #fout.write('CPU '+str(rank)+' running: ' + run_files[j] + ' -- ' + str((tc_end-tc_start)/60.) + '(min) \n')
        fout.write( 'CPU %d running: %s -- %.4f (min) \n' % (rank, run_files[j], (tc_end-tc_start)/60.) )
        fout.flush()
    comm.Barrier()

    if (rank==0) and (num_processes>0):
        time_end=timeit.default_timer()
        fout.write('TOTAL PROCESSING TIME:' + str((time_end-time_start)/60.) + ' (min) \n')
        fout.write('AVERAGE:' + str((time_end-time_start)/60./num_processes) + ' (min/ps) \n')
        fout.write('NUM_SCENE:' + str(num_processes) + ' \n')
        fout.write('---------------------- COMPLETED --------------------------\n')
        fout.write('\n')

    fout.close()
