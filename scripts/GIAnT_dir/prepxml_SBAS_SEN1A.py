#!/usr/bin/env python
'''Example script for creating XML files for use with the SBAS processing chain. This script is supposed to be copied to the working directory and modified as needed.'''

import tsinsar as ts
import argparse
import numpy as np

def parse():
    parser= argparse.ArgumentParser(description='Preparation of XML files for setting up the processing chain. Check tsinsar/tsxml.py for details on the parameters.')
    parser.parse_args()


parse()

infile = open ('example.rsc', 'r')
i=0
for line in infile:
    line = line.strip()
    sline = line.split()
    if i==0:
        width = sline[1]
    if i==1:
        height = sline[1]
    i+=1
infile.close()

ifgfile = open ('ifg.list', 'r')
j=0
for line in ifgfile:
    j+=1
ifgfile.close()


g = ts.TSXML('data')
g.prepare_data_xml('example.rsc', xlim=[0,int(width)], ylim=[0,int(height)], rxlim=None, rylim=None,latfile='lat.flt', lonfile='lon.flt', hgtfile='demfloat32.crop', inc = 21., cohth=0.15, chgendian='False', masktype='f4',unwfmt='RMG', demfmt='FLT', corfmt='RMG', endianlist=['UNW','COR','HGT'])
g.writexml('data.xml')

g = ts.TSXML('params')
g.prepare_sbas_xml(nvalid=int(j*0.8),netramp=True,atmos='',demerr=False,uwcheck=False,regu=True,masterdate='',filt=0.4)
g.writexml('sbas.xml')


############################################################
# Program is part of GIAnT v1.0                            #
# Copyright 2012, by the California Institute of Technology#
# Contact: earthdef@gps.caltech.edu                        #
############################################################
