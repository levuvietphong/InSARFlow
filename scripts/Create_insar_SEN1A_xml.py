#!/usr/bin/env python3
import isce
from isceobj.XmlUtil import FastXML as xml
import os, sys, glob, re
import argparse
from collections import OrderedDict

def cmdLineParse():
    ''' Command Line Parser. '''
    parser = argparse.ArgumentParser(description='Create ALOS input xmlfile for insarApp.py')
    parser.add_argument('-s','--slcdir', type=str, required=False, help='raw data folder root path', dest='slc')
    parser.add_argument('-i','--isce', type=str, required=False, help='isce product folder path', dest='isce')
    parser.add_argument('-a','--aux', type=str, required=False, help='auxilliary folder path', dest='aux')
    parser.add_argument('-l','--link', type=str, required=False, help='AUX link download', dest='link')
    parser.add_argument('-o','--poe', type=str, required=False, help='poeorb folder path', dest='poe')
    parser.add_argument('-p','--selectPairs',type=str, default=None, help='select Pairs', dest='pairs')
    parser.add_argument('-d','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-b','--bound',type=str, default='./', help='bounding box file', dest='bound')
    
    inputs = parser.parse_args()
    if (not inputs.slc):
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

   
def insarApp_SEN1A_xml_generator(slcdir, iscedir, auxdir, poedir, auxlink, dateinfo, demfile, bbox):

    # Initialize a component named isceApp
    topsinsar = xml.Component('topsinsar')
    topsinsar['sensor name'] = 'SENTINEL1'
    for i, v in enumerate(dateinfo):
        master = {} 
        slave = {}
        datepair = re.findall(r"[-+]?\d*\.\d+|\d+", dateinfo[i])
        masterdate = datepair[0]
        slavedate = datepair[1]

        mastersafe = glob.glob(slcdir+'/S1A_IW*' + masterdate + '*') #list
        #master['safe'] = mastersafe
        master['safe'] = list(map(lambda x: '$topdir$/' + str(slcdir) + '/' + os.path.basename(x), mastersafe))
        master['auxiliary data directory'] = '$topdir$/' + str(auxdir) + auxlink[67:] + '/s1a-aux-cal.xml'
        master['orbit directory'] = '$topdir$/' + str(poedir)
        master['output directory'] = 'master' 
        
        slavesafe = glob.glob(slcdir+'/S1A_IW*' + slavedate + '*') #list
        #slave['safe'] = slavesafe
        slave['safe'] = list(map(lambda x: '$topdir$/' + str(slcdir) + '/' + os.path.basename(x), slavesafe))
        slave['auxiliary data directory'] = '$topdir$/' + str(auxdir) + auxlink[67:] + '/s1a-aux-cal.xml'
        slave['orbit directory'] = '$topdir$/' + str(poedir)
        slave['output directory'] = 'slave' 

        topsinsar['master'] = master
        topsinsar['slave'] = slave
        if demfile is not None:
            topsinsar['demFilename'] = demfile

        if bbox is not None:
            topsinsar['region of interest'] = [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])]
        
        topsinsar['swaths'] = [2]
        topsinsar['range looks'] = 7
        topsinsar['azimuth looks'] = 3
        topsinsar['filter strength'] = 0.4
        topsinsar['esd coherence threshold'] = 0.7
        topsinsar['do unwrap'] = 'True'
        topsinsar['unwrapper name'] = 'snaphu_mcf'
        topsinsar['geocode list'] = ['merged/phsig.cor', 'merged/topophase.cor', 'merged/filt_topophase.unw', 'merged/los.rdr', 'merged/topophase.flat', 'merged/filt_topophase.flat']

        if bbox is not None:
            topsinsar['geocode bounding box'] = [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])]

        # Export to topsinsar.xml
        filexml = iscedir+'/'+datepair[0]+'__'+datepair[1]+'/topsApp.xml'
        topsinsar.writeXML(filexml, root='topsApp')
  
        # # Update root dir at current working directory
        with open(filexml, "r") as in_file:
            buf = in_file.readlines()

        with open(filexml, "w") as out_file:
            for line in buf:
                match = re.search(r'<component name="topsinsar">', line.strip(), re.DOTALL)
                if match:
                    line = line + '        <constant name="topdir">'+os.getcwd()+'</constant>\n'
                out_file.write(line)

if __name__ == '__main__':
    '''
    Usage example
    Create_insar_SEN1A_xml.py -r slcdir -i iscedir -p datepairs
    '''

    Data_dir = ''
    if len(sys.argv) == 1:
        print('Create_insar_SEN1A_xml.py -s slcdir -i iscedir -p datepairs')
        sys.exit()
    elif len(sys.argv) > 1:
        inputs = cmdLineParse()
        slcdir = inputs.slc
        iscedir = inputs.isce
        auxdir = inputs.aux
        auxlink = inputs.link
        poedir = inputs.poe
        datepairs = inputs.pairs
        demfile = inputs.dem
        bbox = inputs.bound.split(',')
    
    print('Creating XML files for topsApp processing! \n')
    print('Bounding box for geocode: %s \n' % bbox)
    dateinfo = GetDatePair('.', datepairs)
    insarApp_SEN1A_xml_generator(slcdir, iscedir, auxdir, poedir, auxlink, dateinfo, demfile, bbox)
