import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import gdal
import h5py
import os,sys,shutil,subprocess,glob


def PlotSWBD(list):
    f = open(list.GIAnTDirectory+'/demfloat32.crop.rsc','r')
    content = f.read()  
    lines = content.split("\n")
    for line in lines:
        if len(line.split()) > 0:
            var = line.split()[0]
            if var == "LON_REF2":
                lon_start = float(line.split()[1])
            if var == "LON_REF1":
                lon_end = float(line.split()[1])                        
            if var == "LAT_REF1":
                lat_start = float(line.split()[1])
            if var == "LAT_REF3":
                lat_end = float(line.split()[1])
            if var == "Y_STEP":
                pixelHeight = float(line.split()[1])
            if var == "X_STEP":
                pixelWidth = float(line.split()[1])
    print(lon_start, lon_end, lat_start, lat_end, pixelHeight, pixelWidth)

    swbd = glob.glob(list.ISCEDirectory+'/swbdLat*.wbd.vrt')
    print(swbd[0])
    ds = gdal.Open(swbd[0],gdal.GA_ReadOnly)
    data = ds.GetRasterBand(1).ReadAsArray()
    gt =ds.GetGeoTransform()
    ds = gdal.Translate('new.tif', ds, projWin = [lon_start, lat_start, lon_end, lat_end])
    swbd0 = ds.GetRasterBand(1).ReadAsArray()
    
    return swbd0


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
        data = np.where(coherence >= cohth, 1, 0)
        arr = arr + data

    hf = h5py.File(list.MISCDirectory+'/CoherenceMap_'+str(cohth)+'_.h5', 'w')
    hf.create_dataset('cohthres', data=arr)
    hf.close()


def ExtractUnwrappedPhase(list):
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

    hf0 = h5py.File(list.MISCDirectory+'/UnwPhase.h5', 'w')
    hf0.create_dataset('unwphase', data=unwphase)
    hf0.close()



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



def AnalyzeVelocity(list,unwphf,wlen):
    print('Analyzing Velocity and Deformation')
    pairs = open(list.CompleteList)
    first_ifg = pairs.readline().strip()

    ds = gdal.Open(list.ISCEDirectory+'/'+first_ifg+'/merged/filt_topophase.unw.geo')
    coherence0 = ds.GetRasterBand(1).ReadAsArray()

    hf0 = h5py.File(list.MISCDirectory+'/'+unwphf, 'r')
    unwphase = hf0.get('unwphase')
    deform = unwphase.value * wlen * 10. / (4*np.pi)
    print(type(deform))
    print(np.shape(deform))
    velocity = np.mean(deform, axis=0)
    swbd = PlotSWBD(list)
        
    coherence0[swbd==255] = np.nan
    velocity[swbd==255] = np.nan
    velocity[coherence0==0.] = np.nan

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('jet_r')
    im = ax.imshow(velocity-0.5,cmap=cmap,vmin=-4,vmax=0)
    plt.colorbar(im, shrink=0.5, ax=ax)
    plt.show()



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
    ds = gdal.Open(list.ISCEDirectory+'/'+pair+'/merged/filt_topophase.unw.geo')
    data0 = ds.GetRasterBand(1).ReadAsArray()
    data1 = ds.GetRasterBand(2).ReadAsArray()
    swbd = PlotSWBD(list)
    
    data0[swbd==255] = np.nan
    data1[swbd==255] = np.nan
    data1[data0==0.] = np.nan

    fig, ax = plt.subplots(1,2)
    cmap = plt.get_cmap('jet')

    im0 = ax[0].imshow(np.log10(data0),cmap=plt.get_cmap('gray'))
    plt.colorbar(im0, shrink=0.5, ax=ax[0])
    
    im1 = ax[1].imshow(data1,cmap=cmap)
    plt.colorbar(im1, shrink=0.5, ax=ax[1])
    
    plt.show()
