import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import gdal
import h5py
import os,sys,shutil,subprocess,glob

def load_geom(file,ind):
    ds = gdal.Open(file,gdal.GA_ReadOnly)
    data = ds.GetRasterBand(ind).ReadAsArray()
    return data


