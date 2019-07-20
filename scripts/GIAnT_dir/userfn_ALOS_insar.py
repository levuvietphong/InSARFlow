import os, sys, glob, re

#####s needs to be custom written for your stacks if needed
#####Returns the path to the files.
def makefnames(dates1,dates2,sensor):
    ####Sensor input is ignored in this case
    # dirname = './data'     #Relative path provided. Change to absolute path if needed.
    # iname = '%s/%s-%s.unw.geo'%(dirname,dates1,dates2)
    # cname = '%s/%s-%s.cor.geo'%(dirname,dates1,dates2)
    dirname = '../ISCE'
    root = os.path.join(dirname, dates1+'__'+dates2, 'interferogram')
    iname = os.path.join(root, 'filt_topophase.unw.geo')
    cname = os.path.join(root, 'topophase.cor.geo')
    
    return iname,cname

#####To use for NSBAS
def NSBASdict():
    '''Returns a string representation of the temporal dictionary to be used with NSBAS.'''
    rep = [['POLY',[1],[tims[Ref]]],
	   ['LOG'],[-2.0],[3.0]]  
    return rep

#####To use for timefn invert / MInTS.
def timedict():
   '''Returns a string representation of the temporal dictionary to be used with inversions.'''
   rep = [['ISPLINES',[3],[48]]]
   return rep

############################################################
# Program is part of GIAnT v1.0                            #
# Copyright 2012, by the California Institute of Technology#
# Contact: earthdef@gps.caltech.edu                        #
############################################################

