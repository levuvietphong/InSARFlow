#!/usr/bin/env python3
import isce
from isceobj.XmlUtil import FastXML as xml
import os, sys, glob, re
import argparse
from collections import OrderedDict

def cmdLineParse():
    ''' Command Line Parser. '''
    parser = argparse.ArgumentParser(description='Create ALOS input xmlfile for insarApp.py')
    parser.add_argument('-m','--mode', type=str, required=True, help='mode for processing', dest='mode')
    parser.add_argument('-r','--rawdir', type=str, required=False, help='raw data folder root path', dest='raw')
    parser.add_argument('-i','--isce', type=str, required=False, help='isce product folder path', dest='isce')
    parser.add_argument('-p','--selectPairs',type=str, default=None, help='select Pairs', dest='pairs')
    parser.add_argument('-l','--listxml',type=str, default=None, help='xml file list', dest='list')
    parser.add_argument('-d','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-b','--bound',type=str, default=None, help='bounding box file', dest='bound')

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

    
def insarApp_ALOS_xml_generator(pmode, ALOSraw, iscedir, dateinfo, demfile, bbox):
    
    # Initialize a component named isceApp
    insarApp = xml.Component('insar')
    insarproc = {}

    for i, v in enumerate(dateinfo):
        master = {} 
        slave = {}
        masterd2s = False
        slaved2s  = False
        datepair = re.findall(r"[-+]?\d*\.\d+|\d+", dateinfo[i])
        master_dir = ALOSraw +'/'+ datepair[0]        
        if pmode=='insar':
            ext = '.raw'
        elif pmode=='stripmap':
            ext = ''

        master_imgfile_full = glob.glob(master_dir + '/IMG-HH*')[0]
        master_IMG = '$topdir$/' + master_imgfile_full
        mastersize = os.path.getsize(master_imgfile_full)
        master_ledfile_full = glob.glob(master_dir + '/LED*')[0]
        master_LED = '$topdir$/' + master_ledfile_full
        master['IMAGEFILE'] = master_IMG
        master['LEADERFILE'] = master_LED
        master['output'] = datepair[0] + ext

        slave_dir = ALOSraw +'/'+ datepair[1]
        slave_imgfile_full = glob.glob(slave_dir + '/IMG-HH*')[0]
        slave_IMG = '$topdir$/' + slave_imgfile_full
        slavesize = os.path.getsize(slave_imgfile_full)
        slave_ledfile_full = glob.glob(slave_dir + '/LED*')[0]
        slave_LED = '$topdir$/' + slave_ledfile_full
        slave['IMAGEFILE'] = slave_IMG
        slave['LEADERFILE'] = slave_LED
        slave['output'] = datepair[1] + ext

        if (round(1.0*mastersize/slavesize, 0)==2.0):
            slaved2s = True
        elif (round(1.0*slavesize/mastersize, 0)==2.0):
            masterd2s = True
        
        if masterd2s:
            master['RESAMPLE_FLAG'] = 'dual2single'
        if slaved2s:
            slave['RESAMPLE_FLAG'] = 'dual2single'

        #####Set sub-component
        ####Nested dictionaries become nested components
        insarApp['master'] = master
        insarApp['slave'] = slave

        # ####Set properties, user change
        insarApp['sensor name'] = 'ALOS'
        insarApp['range looks'] = 8
        insarApp['azimuth looks'] = 16
        insarApp['filter strength'] = 0.5
        

        if pmode=='insar':
            #insarproc['applyWaterMask'] = 'False'
            insarApp['insarproc'] = insarproc            
            insarApp['slc offset method'] = 'offsetprf' #'ampcor' #'offsetprf'
            insarApp['unwrap'] = 'True'
            insarApp['unwrapper name'] = 'snaphu_mcf'
            insarApp['geocode list'] = ['filt_topophase.unw','filt_topophase.flat','phsig.cor','topophase.cor','los.rdr','z.rdr','filt_topophase.unw.conncomp']
            if demfile is not None:
                insarApp['dem'] = xml.Catalog(demfile+'.xml')             
        elif pmode=='stripmap':
            insarApp['do denseoffsets'] = 'True'
            insarApp['do split spectrum'] = 'True'
            insarApp['unwrapper name'] = 'snaphu'
            insarApp['do dispersive'] = 'True'
            insarApp['dispersive filter kernel x-size'] = 800
            insarApp['dispersive filter kernel y-size'] = 800
            insarApp['dispersive filter kernel sigma_x'] = 100
            insarApp['dispersive filter kernel sigma_y'] = 100
            insarApp['dispersive filter kernel rotation'] = 0
            insarApp['dispersive filter number of iterations'] = 5
            insarApp['dispersive filter mask type'] = 'connected_components'
            insarApp['dispersive filter coherence threshold'] = 0.6    
            if demfile is not None:
                insarApp['demFilename'] = demfile


        if bbox is not None:
            file = open(bbox)
            for line in file:
                bb = line.split('\t')
                insarApp['geocode bounding box'] = [float(bb[0]), float(bb[1]), float(bb[2]), float(bb[3])]

        # Export to insarApp.xml
        filexml = iscedir+'/'+datepair[0]+'__'+datepair[1]+'/'+pmode+'App.xml'
        insarApp.writeXML(filexml, root='insarApp')

        # # Update root dir at current working directory
        with open(filexml, "r") as in_file:
            buf = in_file.readlines()

        with open(filexml, "w") as out_file:
            for line in buf:
                match = re.search(r'<component name="insar">', line.strip(), re.DOTALL)
                if match:
                    line = line + '        <constant name="topdir">'+os.getcwd()+'</constant>\n'
                out_file.write(line)



if __name__ == '__main__':
    '''
    Usage example
    Create_ALOS_xml.py -r rawdir -i iscedir -c datepairs -o outdir
    '''

    Data_dir = ''
    if len(sys.argv) == 1:
        print('Create_ALOS_xml.py -r rawdir -i iscedir -c datepairs -l list')
        sys.exit()
    elif len(sys.argv) > 1:
        inputs = cmdLineParse()
        pmode = inputs.mode
        ALOSraw = inputs.raw
        iscedir = inputs.isce
        datepairs = inputs.pairs
        demfile = inputs.dem
        bbox = inputs.bound

    if (pmode != 'insar') and (pmode != 'stripmap'):
        print('Error: Wrong processing mode!!! Please select "insar" or "stripmap". \n')
        exit()

    dateinfo = GetDatePair('.', datepairs)
    insarApp_ALOS_xml_generator(pmode, ALOSraw, iscedir, dateinfo, demfile, bbox)
