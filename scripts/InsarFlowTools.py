import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import gdal
import h5py
import os,sys,shutil,subprocess


def ExtractCoherence(list,cohth):
    print('Extracting Coherence')
    pairs = open(list.CompleteList)
    num_scenes = sum(1 for line in pairs)
    pairs = open(list.CompleteList)
    first_ifg = pairs.readline().strip()

    if list.Platform == 'Sentinel-1A':
        ds0 = gdal.Open(list.ISCEDirectory+'/'+first_ifg+'/merged/topophase.cor.geo')
    elif list.Platform == 'ALOS':
        ds0 = gdal.Open(list.ISCEDirectory+'/'+first_ifg+'/topophase.cor.geo')
    
    data = ds0.GetRasterBand(2).ReadAsArray()
    m,n = data.shape

    arr = np.zeros((m,n))
    pairs = open(list.CompleteList)
    for i, line in enumerate(pairs):
        print(i,line)
        pairdir = line.split('\n')[0].strip()
        
        if list.Platform == 'Sentinel-1A':
            fp = list.ISCEDirectory+'/'+first_ifg+'/merged/topophase.cor.geo'
        elif list.Platform == 'ALOS':
            fp = list.ISCEDirectory+'/'+first_ifg+'/topophase.cor.geo'
        
        ds = gdal.Open(fp, gdal.GA_ReadOnly)
        coherence = ds.GetRasterBand(2).ReadAsArray()                
        for j in range(num_scenes):
            data = np.where(coherence >= cohth, 1, 0)
            arr = arr + data

    hf = h5py.File(list.MISCDirectory+'/CoherenceMap_'+str(cohth)+'_.h5', 'w')
    hf.create_dataset('cohthres', data=arr)
    hf.close()


def ExtractUnwrappedPhase(list,wlen):
    print('Extracting Unwrapped Phase...')
    pairs = open(list.CompleteList)
    num_scenes = sum(1 for line in pairs)
    pairs = open(list.CompleteList)
    first_ifg = pairs.readline().strip()

    if list.Platform == 'Sentinel-1A':
        ds0 = gdal.Open(list.ISCEDirectory+'/'+first_ifg+'/merged/filt_topophase.unw.geo')
    elif list.Platform == 'ALOS':
        ds0 = gdal.Open(list.ISCEDirectory+'/'+first_ifg+'/filt_topophase.unw.geo')
    
    data = ds0.GetRasterBand(2).ReadAsArray()
    m,n = data.shape
    unwphase = np.nan*np.zeros((num_scenes,m,n),dtype=np.float32)
    
    pairs = open(list.CompleteList)
    for k, line in enumerate(pairs):
        pairdir = line.split('\n')[0].strip()
        if list.Platform == 'Sentinel-1A':
            fp = list.ISCEDirectory+'/'+first_ifg+'/merged/filt_topophase.unw.geo'
        elif list.Platform == 'ALOS':
            fp = list.ISCEDirectory+'/'+first_ifg+'/filt_topophase.unw.geo'

        ds = gdal.Open(fp, gdal.GA_ReadOnly)
        unwphase[k,:,:] = ds.GetRasterBand(2).ReadAsArray()
        print(k,line)
    
    deform = unwphase * wlen * 10. / (4*np.pi)

    hf0 = h5py.File(list.MISCDirectory+'/UnwPhase.h5', 'w')
    hf0.create_dataset('unwphase', data=unwphase)
    hf0.close()

    hf1 = h5py.File(list.MISCDirectory+'/Deformation.h5', 'w')
    hf1.create_dataset('deform', data=deform)
    hf1.close()
    

def AnalyzeCoherenceAndUnwPhase(list,cohf,unwphf):
    print('Analyzing Coherence and Deformation')

    pairs = open(list.CompleteList)
    num_scenes = sum(1 for line in pairs)

    hf0 = h5py.File(list.MISCDirectory+'/'+cohf, 'r')
    cohth = hf0.get('cohthres')            
    
    hf1 = h5py.File(list.MISCDirectory+'/'+unwphf,'r')
    unwphase = hf1.get('unwphase')
    t,m,n = unwphase.shape
    stdarr = np.nanstd(unwphase, axis=0)


def Plotting(list,h5f,var,opt,ind):
    hf = h5py.File(list.MISCDirectory+'/'+h5f, 'r')
    data = hf.get(var)
    if opt == 0:
        vel = data[ind,:,:]
    else:
        vel = np.mean(data,axis=0)

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')
    im = ax.imshow(vel,cmap=cmap)
    plt.colorbar(im, shrink=0.5, ax=ax)
    plt.show()


def PlotIFGs(list,pair):
    ds0 = gdal.Open(list.ISCEDirectory+'/'+pair+'/merged/filt_topophase.unw.geo')
    data = ds0.GetRasterBand(2).ReadAsArray()
    #data[data>10000] = np.nan
    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')
    im = ax.imshow(data,cmap=cmap)
    plt.colorbar(im, shrink=0.5, ax=ax)
    plt.show()