#!/usr/bin/env python3

import isce
from isceobj.XmlUtil import FastXML as xml
import os, sys, glob, re
import argparse
from collections import OrderedDict


def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Download SBWD files from USGS')
    parser.add_argument('-i','--isce', type=str, required=False, help='isce product folder path', dest='isce')
    parser.add_argument('-d','--dem',type=str, default=None, help='DEM filename', dest='dem')
    inputs = parser.parse_args()
    return inputs


def swbd_xml_generator(minLat,maxLat,minLon,maxLon, iscedir):
    swbd = xml.Component('wbdstitcher')
    water = {} 
    water['action'] = 'stitch'
    water['bbox'] = [minLat,maxLat,minLon,maxLon]
    water['keepWbds'] = True
    water['noFilling'] = False
    swbd['wbd stitcher'] = water
    swbd.writeXML(iscedir+'/input_swbd.xml', root='stitcher')


def get_bounding_box(demfile):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", demfile)
    
    if demfile[7] == 'N':
        minLat = int(numbers[0])
    else:
        minLat = -int(numbers[0])

    if demfile[11] == 'N':
        maxLat = int(numbers[1])
    else:
        maxLat = -int(numbers[1])

    if demfile[19] == 'E':
        minLon = int(numbers[2])
    else:
        minLon = -int(numbers[2])

    if demfile[24] == 'E':
        maxLon = int(numbers[3])
    else:
        maxLon = -int(numbers[3])
    
    return minLat,maxLat,minLon,maxLon


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Number of arguments: %d' % len(sys.argv))
        print('Error in Generate_SWBD_xml.py: Number of arguments is not matched!')
        sys.exit()
    elif len(sys.argv) > 1:
        inputs = cmdLineParse()
        iscedir = inputs.isce
        demfile = inputs.dem
    
    minLat,maxLat,minLon,maxLon = get_bounding_box(demfile)
    swbd_xml_generator(minLat,maxLat,minLon,maxLon,iscedir)
