#!/usr/bin/env python3

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def plot_network():
    df_pair = pd.read_csv('ifg.list',sep='\t',names=['Master','Slave','Relative Height','Sensor'])
    height_tab = pd.read_csv('Baseline_table.csv')
    dfa = pd.DataFrame(columns=['Master','Slave','Height Master','Height Slave'])

    num = df_pair.shape[0]
    for i in range(0,num):
        master = df_pair.iloc[i]['Master']
        slave = df_pair.iloc[i]['Slave']
        
        ind = height_tab['Scenes']==master
        jm = np.where(ind==True)[0][0]
        height_master = height_tab.iloc[jm]['Relative Height']
        
        ind = height_tab['Scenes']==slave
        js = np.where(ind==True)[0][0]
        height_slave = height_tab.iloc[js]['Relative Height']
        
        df = pd.DataFrame([[master, slave, height_master, height_slave]],
                        columns=['Master','Slave','Height Master','Height Slave'])
        dfa = dfa.append(df, ignore_index=True)

    dfa['Master'] = pd.to_datetime(dfa['Master'], format='%Y%m%d')
    dfa['Slave'] = pd.to_datetime(dfa['Slave'], format='%Y%m%d')

    plt.figure(figsize=(14,7))
    for i in range(0,num):
        x = [dfa.iloc[i]['Master'],dfa.iloc[i]['Slave']]
        y = [dfa.iloc[i]['Height Master'],dfa.iloc[i]['Height Slave']]
        plt.plot(x, y, marker='o', markerfacecolor='red',lw=1,color='k')
        plt.ylabel('Perpendicular Baseline [m]')
        plt.xlabel('Time')
    
    dirpath = os.getcwd()
    foldername = os.path.basename(dirpath)
    plt.savefig(foldername + '.png')
    plt.savefig('../' + foldername + '.png')

if __name__ == '__main__':    
    plot_network()
