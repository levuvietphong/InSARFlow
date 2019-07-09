import numpy as np
import pandas as pd 
import subprocess
import gdal, ogr, os, osr
import h5py
from datetime import date


def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


if __name__ == '__main__':
    data = pd.read_csv('Mekong_ASF.csv')
    path = np.array([477,478,479,480,481])
    path481=[170,160]
    path480=[200,190,180,170,160]
    path479=[200,190,180,170]
    path478=[200,190,180,170]
    path477=[200,190,180]

    # path481=[170,160]
    # path480=[200,190,180,170,160]
    # path479=[200,190,180,170]
    # path478=[200,190,180,170]
    # path477=[200,190,180]

    path481.extend([np.nan]*3)
    path479.extend([np.nan]*1)
    path478.extend([np.nan]*1)
    path477.extend([np.nan]*2)
    sar = pd.DataFrame({'481':path481,'480':path480,'479':path479,'478':path478,'477':path477}) 
    run_script = True

    flog = open('log_geocode.txt',"a")
    for path in sar.columns:
        frames = sar[path]
        for frame in frames:
            if ~np.isnan(frame):
                print('RUNNING PATH: ' + str(path) + ' AND FRAME: ' + str(int(frame)))
                flog.write('RUNNING PATH: ' + str(path) + ' AND FRAME: ' + str(int(frame)) + '\n')
                flog.flush()
                directory = 'P'+path+'_F'+str(int(frame))+'/GIAnT'
                if not os.path.exists(directory):
                    print("Error: GIAnT folder does NOT exist")
                    flog.write('Error: GIAnT folder does NOT exist \n')
                    flog.flush()
                    exit()

                if run_script:
                    cwd = os.getcwd()
                    os.chdir(directory)
                    # Read csv file for origin, resolution, width, and height of the image
                    df = pd.read_csv('Baseline_stats.csv')
                    rasterOrigin = (df.iloc[0]['lon_start'],df.iloc[0]['lat_start'])
                    pixelWidth = df.iloc[0]['lon_delta']
                    pixelHeight = df.iloc[0]['lat_delta']
                    newRasterfn = 'P'+path+'_F'+str(int(frame))+'.tif'
                    
                    # Load h5 data and make average
                    hf = h5py.File('Stack/LS-PARAMS.h5', 'r')
                    dates = hf.get('dates')
                    tims = hf.get('tims')
                    recons = hf.get('recons')
                    mean_vel = (recons.value[-1,:,:] - recons.value[0,:,:])/tims.value[-1]
                    mean_vel[np.isnan(mean_vel)] = -9999
                    array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,mean_vel)
                    cmd = 'cp ' + newRasterfn + ' ' + cwd + '/TIFFs'
                    subprocess.call(cmd, shell=True)
                    os.chdir(cwd)
    flog.close()
