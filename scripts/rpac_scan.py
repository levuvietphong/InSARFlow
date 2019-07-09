#!/usr/bin/env python

import os, sys, glob, re
import argparse
import datetime
import lxml.objectify as ob
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import subprocess
import shutil

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Processing ISCE product to create example.rsc')
    parser.add_argument('-l','--list', type=str, required=True, help='List of folders containing insarProc.xml files', dest='list')
    parser.add_argument('-d','--dir', type=str, required=True, help='GIAnT directory', dest='dir')    
    parser.add_argument('-b','--bounding', type=str, required=True, help='Bounding box file for geocoding', dest='bound')
    parser.add_argument('-c','--crop', type=int, required=True, help='Number of rows and columns cropped', dest='crop')    
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

def extract_baseline(filexml):        
    fin = open(filexml,'r')
    inp = ob.fromstring(fin.read())
    bsln = np.float(inp.baseline.perp_baseline_bottom)
    return bsln



if __name__ == '__main__':
    if len(sys.argv) != 9:
        print('rpac_scan.py -l list -d giant -b bbox -c num_crop')
        sys.exit()
    else:
        inputs = cmdLineParse()
        insar_xml_list = inputs.list
        giant_dir = inputs.dir
        bbox_file = inputs.bound
        num_crop = inputs.crop

    num = len(insar_xml_list)
    scene_full = []
    file = open(insar_xml_list)
    df = pd.DataFrame()
    for line in file:
        scene = line.split('\n')[0]
        datepair = re.findall(r"[-+]?\d*\.\d+|\d+", scene)
        proc_list = scene.split()[0]+'/insarProc.xml'
        geo_list = scene.split()[0]+'/filt_topophase.unw.geo.xml'
        scene_full.append(scene)

        hdg, wvl, utc = extract_proc(proc_list)
        width, length, lon_delta, lon_start, lon_end, lat_delta, lat_start, lat_end = extract_geoxml(geo_list) 
        print(width,length,hdg,wvl,utc,scene.split()[0])
        baseline = extract_baseline(proc_list)
        data = np.column_stack((datepair[0], datepair[1], hdg, wvl, utc, width, length, lon_delta, lon_start, lon_end, lat_delta, lat_start, lat_end))
        dfs = pd.DataFrame(data, columns=['master','slave','hdg', 'wvl', 'utc', 'width', 'length', 'lon_delta', 'lon_start', 'lon_end', 'lat_delta', 'lat_start', 'lat_end'])
        df=df.append(dfs)
            
    df.to_csv(giant_dir+'/Baseline_stats.csv', index=False)
    
    xmin = float(df['lon_start'].max()) + lon_delta*num_crop
    xmax = float(df['lon_end'].min()) - lon_delta*num_crop
    ymin = float(df['lat_end'].max()) - lat_delta*num_crop
    ymax = float(df['lat_start'].min()) + lat_delta*num_crop
    width = int(df.iloc[0]['width'])
    file_length = int(df.iloc[0]['length'])
    heading_dec = float(df.iloc[0]['hdg'])
    wavelength = float(df.iloc[0]['wvl'])
    center_utc = int(df.iloc[0]['utc'])
    lat_delta = float(df.iloc[0]['lat_delta'])
    lon_delta = float(df.iloc[0]['lon_delta'])

    # Create a bounding box file 
    fout= open(giant_dir+'/'+bbox_file,"w")
    fout.write(str(ymin) + '\t' + str(ymax) + '\t' + str(xmin) + '\t' + str(xmax) + '\n')
    fout.close()
    print(bbox_file + ' file has been created.')

    # Create example.rsc file
    fout= open(giant_dir+'/example.rsc',"w")
    fout.write('WIDTH'+'\t'+'\t'+'\t'+str(width)+'\n')
    fout.write('FILE_LENGTH'+'\t'+'\t'+'\t'+str(file_length)+'\n')
    fout.write('HEADING_DEG'+'\t'+'\t'+'\t'+str(heading_dec)+'\n')
    fout.write('CENTER_LINE_UTC'+'\t'+'\t'+'\t'+str(center_utc)+'\n')
    fout.write('WAVELENGTH'+'\t'+'\t'+'\t'+str(wavelength)+'\n')
    fout.close()
    print(giant_dir+'/example.rsc file has been created.')


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
    lat=np.zeros([length,width])
    lon=np.zeros([length,width])
    for i in range(0,length):
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