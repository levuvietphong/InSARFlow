#!/usr/bin/env python3

import os, sys, glob, re
import argparse
import datetime
import lxml.objectify as ob
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import gdal
import subprocess
import shutil

sys.path.insert(0, os.environ["ISCE_ROOT"]+'/isce/components')
from iscesys.Component.ProductManager import ProductManager as PM
pm = PM()
pm.configure()


def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Processing ISCE product to create example.rsc')
    parser.add_argument('-l','--list', type=str, required=True, help='List of folders containing insarProc.xml files', dest='list')
    parser.add_argument('-i','--iscedir', type=str, required=True, help='ISCE directory', dest='iscedir')    
    parser.add_argument('-g','--gdir', type=str, required=True, help='GIAnT directory', dest='gdir')    
    inputs = parser.parse_args()    
    return inputs


def extract_proc(filexml):
    fin = open(filexml,'r')
    inp = ob.fromstring(fin.read())  
    hdg = np.float(inp.runGeocode.inputs.peg_heading) * 180.0/np.pi
    wvl = np.float(inp.runGeocode.inputs.radar_wavelength)
    utc1 = datetime.datetime.strptime(str(inp.master.frame.sensing_start), '%Y-%m-%d %H:%M:%S.%f')
    utc = 3600*utc1.hour + 60*utc1.minute + utc1.second

    return hdg, wvl, utc

def extract_geoxml(filexml):
    tree = ET.parse(filexml)
    root = tree.getroot()
    for prop in root.findall('property'):
        name = prop.get('name')
        if name=='width':
            width = int(prop.find('value').text)
        if name=='length':
            length = int(prop.find('value').text)        
    
    for prop in root.findall('component'):        
        name = prop.get('name')
        if name=='coordinate1':
            for coor in prop.findall('property'):
                name2 = coor.get('name')
                if name2=='delta':
                    lon_delta = float(coor.find('value').text)        
                if name2=='startingvalue':
                    lon_start = float(coor.find('value').text)        
                if name2=='endingvalue':
                    lon_end = float(coor.find('value').text)        
        if name=='coordinate2':
            for coor in prop.findall('property'):
                name2 = coor.get('name')
                if name2=='delta':
                    lat_delta = float(coor.find('value').text)        
                if name2=='startingvalue':
                    lat_start = float(coor.find('value').text)        
                if name2=='endingvalue':
                    lat_end = float(coor.find('value').text)        
    return width, length, lon_delta, lon_start, lon_end, lat_delta, lat_start, lat_end

def ExtractPerpBaseline(iscelog):
	bperp_iw = np.full(6, np.nan, dtype=float)
	
	rfile = open(iscelog, "r")	
	cnt = rfile.readlines()	
	rfile.close()
				
	for line in cnt:
		if line[:57] == 'baseline.IW-1 Bperp at midrange for first common burst = ':
			bperp_iw[0] = float(line[57:])
		elif line[:57] == 'baseline.IW-2 Bperp at midrange for first common burst = ':
			bperp_iw[2] = float(line[57:])
		elif line[:57] == 'baseline.IW-3 Bperp at midrange for first common burst = ':
			bperp_iw[4] = float(line[57:])
			
		if line[:56] == 'baseline.IW-1 Bperp at midrange for last common burst = ':
			bperp_iw[1] = float(line[56:])
		elif line[:56] == 'baseline.IW-2 Bperp at midrange for last common burst = ':
			bperp_iw[3] = float(line[56:])
		elif line[:56] == 'baseline.IW-3 Bperp at midrange for last common burst = ':
			bperp_iw[5] = float(line[56:])
	
	return np.nanmean(bperp_iw)	

def ReadWidthLength(filexml):
    tree = ET.parse(filexml)
    root = tree.getroot()
    for prop in root.findall('property'):
        name = prop.get('name')
        if name=='width':
            width = int(prop.find('value').text)
        if name=='length':
            length = int(prop.find('value').text)

    for prop in root.findall('component'):        
        name = prop.get('name')
        if name=='coordinate1':
            for coor in prop.findall('property'):
                name2 = coor.get('name')
                if name2=='delta':
                    lon_delta = float(coor.find('value').text)        
                if name2=='startingvalue':
                    lon_start = float(coor.find('value').text)        
                if name2=='endingvalue':
                    lon_end = float(coor.find('value').text)        
        if name=='coordinate2':
            for coor in prop.findall('property'):
                name2 = coor.get('name')
                if name2=='delta':
                    lat_delta = float(coor.find('value').text)        
                if name2=='startingvalue':
                    lat_start = float(coor.find('value').text)        
                if name2=='endingvalue':
                    lat_end = float(coor.find('value').text)  
    lon_end = lon_start + lon_delta * width
    return width, length, lon_delta, lon_start, lon_end, lat_delta, lat_start, lat_end

def ReadOtherVars(filexml):
    frame = pm.loadProduct(filexml)	
    burst = frame.bursts[0]	# Obtain the first burst in the frame
    orbit = burst.orbit
    tmid  = frame.sensingMid
    utc   = 3600 * tmid.hour + 60 * tmid.minute + tmid.second  # UTC time
    wvlen = burst.radarWavelength # Wave length
    hdg   = orbit.getHeading(tmid) # heading angle
    return wvlen, hdg, utc



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('PrepareRoipac_SEN1A.py -l list -i isce -g giant')
        sys.exit()
    else:
        inputs = cmdLineParse()
        insar_xml_list = inputs.list
        isce_dir = inputs.iscedir
        giant_dir = inputs.gdir

    fifg= open(giant_dir+'/ifg.list',"w")    
    num = len(insar_xml_list)
    scene_full = []
    file = open(insar_xml_list)
    for line in file:
        scene = line.split('\n')[0]
        datepair = re.findall(r"[-+]?\d*\.\d+|\d+", scene)
        # Extract perp. bsln information
        perp_bsln = ExtractPerpBaseline(isce_dir+'/'+scene+'/isce.log')
        fifg.write('%s \t %s \t %10.4f \t %s \n' % (datepair[0],datepair[1],perp_bsln,'SENT-1A'))
        scene_full.append(scene)
    fifg.close()
    print(giant_dir+'/ifg.list has been created!!!')

    # Read GIAnT info
    fout= open(giant_dir+'/example.rsc',"w")    
    mergdir = isce_dir+'/'+scene_full[0]+'/merged'
    filtxml = None
    if os.path.isdir(mergdir) and os.path.isfile(mergdir + '/' + 'filt_topophase.unw.geo.xml'):
        filtxml = mergdir + '/' + 'filt_topophase.unw.geo.xml'
        width,file_length,lon_delta,lon_start,lon_end,lat_delta,lat_start,lat_end = ReadWidthLength(filtxml) 
    
    xmin = lon_start
    xmax = lon_end
    ymin = lat_end
    ymax = lat_start

    mstdir = isce_dir+'/'+scene_full[0]+'/master'
    iwfile = None
    if os.path.isdir(mstdir):			
        if os.path.isfile(mstdir + '/' + 'IW1.xml'):
            iwfile = mstdir + '/' + 'IW1.xml'
        elif os.path.isfile(mstdir + '/' + 'IW2.xml'):
            iwfile = mstdir + '/' + 'IW2.xml'
        elif os.path.isfile(mstdir + '/' + 'IW3.xml'):
            iwfile = mstdir + '/' + 'IW3.xml'
            
        if iwfile != None:				
            wavelength, heading_dec, center_utc = ReadOtherVars(iwfile)
        else:
            print('Error: Empty IWx.xml files!!!')

    
    fout.write('WIDTH'+'\t'+'\t'+'\t'+str(width)+'\n')
    fout.write('FILE_LENGTH'+'\t'+'\t'+'\t'+str(file_length)+'\n')
    fout.write('HEADING_DEG'+'\t'+'\t'+'\t'+str(heading_dec)+'\n')
    fout.write('CENTER_LINE_UTC'+'\t'+'\t'+'\t'+str(center_utc)+'\n')
    fout.write('WAVELENGTH'+'\t'+'\t'+'\t'+str(wavelength)+'\n')
    fout.close()
    print(giant_dir+'/example.rsc file has been created.')

    # Cropping dem
    cwd = os.getcwd()
    os.chdir(mergdir)
    cmd = "cp demfloat32* " + cwd +"/"+ giant_dir
    subprocess.call("imageMath.py -e a --a dem.crop -s BIL -t float32 -o demfloat32.crop", shell=True)
    subprocess.call(cmd, shell=True)
    os.chdir(cwd)

    # Create demfloat32.crop.rsc file
    fout= open(giant_dir+'/demfloat32.crop.rsc',"w")
    fout.write('WIDTH'+'\t'+'\t'+'\t'+str(width)+'\n')
    fout.write('FILE_LENGTH'+'\t'+'\t'+'\t'+str(file_length)+'\n')
    fout.write('XMIN'+'\t'+'\t'+'\t'+str(0)+'\n')
    fout.write('XMAX'+'\t'+'\t'+'\t'+str(width-1)+'\n')
    fout.write('YMIN'+'\t'+'\t'+'\t'+str(0)+'\n')
    fout.write('YMAX'+'\t'+'\t'+'\t'+str(file_length-1)+'\n')
    fout.write('X_FIRST'+'\t'+'\t'+'\t'+str(xmin)+'\n')
    fout.write('Y_FIRST'+'\t'+'\t'+'\t'+str(ymin)+'\n')
    fout.write('X_STEP'+'\t'+'\t'+'\t'+str(lon_delta)+'\n')
    fout.write('Y_STEP'+'\t'+'\t'+'\t'+str(lat_delta)+'\n')
    fout.write('AZIMUTH_PIXEL_SIZE'+'\t'+'\t'+'\t'+str(np.abs(lon_delta))+'\n')
    fout.write('RANGE_PIXEL_SIZE'+'\t'+'\t'+'\t'+str(np.abs(lon_delta))+'\n')
    fout.write('X_UNIT degrees' + '\n')
    fout.write('Y_UNIT degrees' + '\n')
    fout.write('Z_SCALE 1' + '\n')
    fout.write('Z_OFFSET 0' + '\n')
    fout.write('DATUM WGS84' + '\n')
    fout.write('PROJECTION LATLON' + '\n')

    fout.write('LAT_REF1'+'\t'+'\t'+'\t'+str(ymax)+'\n')
    fout.write('LON_REF1'+'\t'+'\t'+'\t'+str(xmax)+'\n')
    fout.write('LAT_REF2'+'\t'+'\t'+'\t'+str(ymax)+'\n')
    fout.write('LON_REF2'+'\t'+'\t'+'\t'+str(xmin)+'\n')
    fout.write('LAT_REF3'+'\t'+'\t'+'\t'+str(ymin)+'\n')
    fout.write('LON_REF3'+'\t'+'\t'+'\t'+str(xmin)+'\n')
    fout.write('LAT_REF4'+'\t'+'\t'+'\t'+str(ymin)+'\n')
    fout.write('LON_REF4'+'\t'+'\t'+'\t'+str(xmax)+'\n')
    fout.close()
    print(giant_dir+'/demfloat32.crop.rsc file has been created.')

    # Create lat.flt and lon.flt
    lat=np.zeros([file_length,width])
    lon=np.zeros([file_length,width])
    for i in range(0,file_length):
        lat[i,:] = ymin + i*lat_delta
    lat = lat.astype(np.float32)
    with open(giant_dir+'/lat.flt', 'w') as f:
        lat.tofile(f)

    for j in range(0,width):
        lon[:,j] = xmin + j*lon_delta
    lon = lon.astype(np.float32)
    with open(giant_dir+'/lon.flt', 'w') as f:
        lon.tofile(f)
    print('lat.flt and lon.flt files have been created.')

    # Create mask file
    swbd = glob.glob(isce_dir+'/swbdLat*.wbd.vrt')
    ds = gdal.Open(swbd[0],gdal.GA_ReadOnly)
    data = ds.GetRasterBand(1).ReadAsArray()
    gt =ds.GetGeoTransform()
    ds = gdal.Translate(giant_dir+'/watermask.tif', ds, projWin = [xmin, ymax, xmax, ymin])
    wmask = ds.GetRasterBand(1).ReadAsArray()
    wmask = np.ones(wmask.shape) - wmask
    wmaskf4 = wmask.astype('float32')
    wmaskint = wmask.astype(int)
    with open(giant_dir+'/watermask_f4.flt', 'w') as f:
        wmaskf4.tofile(f)
    with open(giant_dir+'/watermask_int.flt', 'w') as f:
        wmaskint.tofile(f)        
    
    print('watermask_f4.flt and watermask_int.flt files have been created.')

    # Copy file to GIAnT folder
    dir_path = os.path.dirname(os.path.dirname(__file__))
    userfn = 'userfn_SEN1A.py'
    
    shutil.copy2(dir_path+'/scripts/GIAnT_dir/'+userfn,giant_dir+'/userfn.py')
    shutil.copy2(dir_path+'/scripts/GIAnT_dir/prepxml_SBAS_SEN1A.py',giant_dir)