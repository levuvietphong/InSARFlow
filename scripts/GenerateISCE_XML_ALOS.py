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
    parser = argparse.ArgumentParser(description='Create ALOS input xml files for ISCE')
    parser.add_argument('-m','--mode', type=str, required=True, help='mode used for processing', dest='mode')    
    parser.add_argument('-r','--rawdir', type=str, required=True, help='raw data folder root path', dest='raw')
    parser.add_argument('-i','--isce', type=str, required=False, help='isce product folder path', dest='isce')
    parser.add_argument('-c','--dateIDfile', type=str, required=False, help='file to convert fileID to dates', dest='dates')
    parser.add_argument('-p','--selectPairs',type=str, required=False, help='select Pairs', dest='pairs')
    parser.add_argument('-d','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-b','--bbox',type=str, default=None, help='Bounding box for DEM and SWBD', dest='bbox')

    inputs = parser.parse_args()
    if (not inputs.raw):
        print('Error!!! No raw data path is provided.')
        sys.exit(0)    
    return inputs


def GetDateID(data_root, datefile):
    '''
    Generating date_list for ALOS isceApp.xml
    Credit: J. Chen @NCL
    -----------------------------------------
    Args:
        data_root: unzipped L1.0 data folder
        datefile:  dateID.info 

    Returns:
        date_list: orbID    date    original_name
    '''
    date_list = []
    datefile_full = data_root + '/' + datefile
    file = open(datefile_full)
    for line in file:
        date = line.split('\n')[0]
        date_list.append(date.split())
    return date_list


def GetDatePair(work_dir, datePairFile):
    '''
    Generation of date pairs for isceApp.xml
    Credit: J. Chen @NCL
    ----------------------------------------- 
    
    Args:
        work_dir: processing directory, also datepair file direcotry
        datePairFile: datePair
    Returns:
        datepair_list: date1/date2,date1/date3
    '''
    datepair_list = []
    datepairfile_full = work_dir + '/' + datePairFile
    file = open(datepairfile_full)
    for line in file:
        datepair = line.split('\n')[0]
        datepair_list.append(datepair)
    return datepair_list

    
def isceApp_ALOS_xml_generator(data_root, date_list, datepairs, outdir, demfile):
    
    # Initialize a component named isceApp
    isceApp = xml.Component('isce')

    # Stack component
    stack = OrderedDict()
    reference_scene = ''
    scene_list=[]
    for i, v in enumerate(date_list):
        hh_date = []
        LEADERFILE_date = []
        scene = data_root +'/'+ v[1]
        imgfile_full = glob.glob(scene + '/IMG-HH*')[0]
        imgfile_name = os.path.split(imgfile_full)[1]
        HHFILE_name = '$rawdir$/' + imgfile_full
        hh_date.append(HHFILE_name)
        ledfile_full = glob.glob(scene + '/LED*')[0]
        ledfile_name = os.path.split(ledfile_full)[1]
        LEADERFILE_name = '$rawdir$/' + ledfile_full
        LEADERFILE_date.append(LEADERFILE_name)

        scene_comp_name = 'scene' + str(i+1)
        scene_i = OrderedDict()
        scene_i['id'] = "\'" + v[1] + "\'"
        scene_i['hh'] = hh_date
        scene_i['LEADERFILE'] = LEADERFILE_date
        if i==0:
            reference_scene = "'"+v[1]+"'"
        scene_i['RESAMPLE_FLAG'] = 'single2dual'
        stack[scene_comp_name] = scene_i
        scene_list.append(v[1])

    #####Set sub-component
    ####Nested dictionaries become nested components
    isceApp['stack'] = stack
    
    # ####Set properties, user change
    isceApp['selectPols'] = 'hh'
    isceApp['sensor name'] = 'ALOS'
    isceApp['resamp range looks'] = 4
    isceApp['resamp azimuth looks'] = 10
    isceApp['slc rangelooks'] = 2
    isceApp['slc azimuthlooks'] = 5
    isceApp['filter strength'] = 0.5
    #isceApp['slc offset method'] = 'ampcor'
    isceApp['coregistration strategy'] = 'single reference'
    isceApp['reference scene'] = reference_scene
    isceApp['output directory'] = '$rawdir$/'+outdir
    
    ####Set steps, no change
    isceApp['do preprocess'] = 'True'
    isceApp['selectScenes'] = scene_list
    if demfile is None:
        isceApp['do verifyDEM'] = 'True'

    # Update pairs of IFGs
    if datepairs is not None:
        isceApp['selectPairs'] = datepairs

    # Export to isceApp.xml
    isceApp.writeXML('isceApp.xml', root='isceApp')

    # Update root dir at current working directory
    with open('isceApp.xml', "r") as in_file:
        buf = in_file.readlines()

    with open('isceApp.xml', "w") as out_file:
        for line in buf:
            match = re.search(r'<component name="isce">', line.strip(), re.DOTALL)
            if match:
                line = line + '        <constant name="rawdir">'+os.getcwd()+'</constant>\n'
            out_file.write(line)


def swbd_xml_generator(bbox, outdir):
    swbd = xml.Component('wbdstitcher')
    water = {} 
    water['action'] = 'stitch'
    water['bbox'] = [int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])]
    water['keepWbds'] = True
    water['noFilling'] = False
    swbd['wbd stitcher'] = water
    swbd.writeXML(outdir+'/input_swbd.xml', root='stitcher')


if __name__ == '__main__':
    if len(sys.argv) < 9:
        print('Number of arguments: %d \n' % len(sys.argv))
        print('Error in Generate_XML_ALOS.py: Number of arguments is not matched!')
        sys.exit()
    elif len(sys.argv) > 1:
        inputs = cmdLineParse()
        mode = inputs.mode
        rawdir = inputs.raw
        datefile = inputs.dates
        datepairs = inputs.pairs
        bbox = inputs.bbox.split(',')
        iscedir = inputs.isce
        demfile = inputs.dem

    date_list = GetDateID(rawdir, datefile)    
    if datepairs is not None:
        datepair_list = GetDatePair('.', datepairs)
    else:
        datepair_list = None

    isceApp_ALOS_xml_generator(rawdir, date_list, datepair_list, iscedir, demfile)
    #swbd_xml_generator(bbox,iscedir)