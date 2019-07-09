#!/usr/bin/env python3

import os, sys, glob, re
import argparse
import numpy as np
import pandas as pd
import shutil
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Checking temporal and spatial baseline for pair selection')
    parser.add_argument('-i','--input', type=str, required=True, help='input file for baseline estimation', dest='input')
    parser.add_argument('-d','--iscedir', type=str, required=True, help='ISCE directory', dest='isce')
    parser.add_argument('-t','--temp', type=float, required=True, help='temporal baseline for pairing', dest='temp')
    parser.add_argument('-p','--pairlist',type=str, required=True, help='export list of pairs to file', dest='pairs')
    arg = parser.parse_args()
    
    return arg


def baseline_check(Graph,temp_thres,perp,datepd,scenes,num_scene):
    """
    Check the temporal baseline of each pair
    Add satisfied pairs to graph G
    """
    for i in range(0,num_scene-1):
        for j in range(i+1, num_scene):
            # Convert to pandas format
            date_master = datepd[i]
            date_slave = datepd[j]
            temp_bsln = np.abs((date_slave-date_master)/np.timedelta64(1, 'D'))

            # Check baseline conditions
            if temp_bsln<temp_thres:
                #print("Pair: {} & {}, temp: {} (days)".format(date_master.date(), date_slave.date(), int(temp_bsln)))
                Graph.add_edge(scenes[i],scenes[j],perpbsln=perp[i]-perp[j])


# This function optimizes the network of interferograms.
# The aim is to ensure degree of connectivity at each nodes
# but the minimize the number of edges among nodes.
def optimize_pairs(G,scenes,heights,i,temp_thres):
    scenes2 = [x for j,x in enumerate(scenes) if (j!=i)]
    heights2 = [x for j,x in enumerate(heights) if (j!=i)]
    
    temp = 50      # days
    perp = 200      # meter

    d = G.degree(scenes[i])
    iter = 0
    while (d < 5) and (iter<100):
        for j in range (0,len(scenes2)):
            perp_bsln = heights2[j] - heights[i]
            date_master = datepd[i]
            date_slave = datepd[j]
            temp_bsln = np.abs((date_slave-date_master)/np.timedelta64(1, 'D'))
            if (temp_bsln<temp):
                G.add_edge(scenes[i],scenes2[j],perpbsln=perp_bsln)
            else:
                temp = temp + (iter%2) * temp*0.05
                if temp > temp_thres:
                    temp = temp_thres
            d = G.degree(scenes[i])
        iter+=1

        
        
if __name__ == '__main__':    
    if len(sys.argv) != 9:
        print('Baseline_SEN1A_check.py -i input -d iscedir -p pairfile -t temp')
        sys.exit()
    else:
        args = cmdLineParse()
        infile = args.input
        iscedir = args.isce
        pairfile = args.pairs
        temp_bsln = args.temp

    # Get Scene names and heights
    df = pd.read_csv(infile)

    scenes = df['Granule Name']
    datepd = pd.to_datetime(df['Acquisition Date'])
    date = datepd.dt.year + (datepd.dt.month-1)/12. + (datepd.dt.day-1)/365.
    num_scene = df.shape[0]

    # The perpendicular heights are unknown. A random array is temporarily assigned.
    # The actual perp. baseline will be calculated later. Here, only temporal baseline is used.
    heights = np.zeros(num_scene)
    scenes = [None] * num_scene

    G = nx.Graph()
    for i in range(0,num_scene):
        if datepd.dt.month[i]<10:
            mon_str = '0'+str(datepd.dt.month[i])
        else:
            mon_str = str(datepd.dt.month[i])

        if datepd.dt.day[i]<10:
            day_str = '0'+str(datepd.dt.day[i])
        else:
            day_str = str(datepd.dt.day[i])            

        scenes[i] = str(datepd.dt.year[i])+mon_str+day_str
        heights[i] = 150. * np.random.uniform(-1,1) # Perp. height will be from -150 to 150
        G.add_node(scenes[i],pos=(date[i],heights[i]))

    # Adding egdes satisfying thresholds
    baseline_check(G,temp_bsln,heights,datepd,scenes,num_scene)

    # Optimize interferogram network
    for i in range(0,num_scene):
        optimize_pairs(G,scenes,heights,i,temp_bsln)

    """
    # Plotting pseudo inteferogram networks
    #######################################
    plt.figure(figsize=(12,6))
    pos=nx.get_node_attributes(G,'pos')
    nx.draw_networkx_nodes(G, pos, node_size=30, node_color="red", with_labels=False)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    plt.xlabel('Date Acquisition')
    plt.ylabel('Perp. Baseline')
    
    dirpath = os.getcwd()
    foldername = os.path.basename(dirpath)
    plt.savefig(foldername + '.png')
    """
    
    # Export list of pairs
    ifglist = open(pairfile, "w")

    num_egdes = G.number_of_edges()
    for d in range(0,num_egdes):
        master = list(G.edges())[d][0]
        slave = list(G.edges())[d][1]
        pair_names = master+'__'+slave
        #print(pair_names)
        ifglist.write("%s\n" % pair_names)
        try:  
            os.mkdir(iscedir+'/'+pair_names)
        except OSError:  
            print ("Folder %s already exists! Skipped" % (iscedir+'/'+pair_names))

    ifglist.close()        

    print('Number of images: ' + str(num_scene))
    print('Number of pairs: ' + str(num_egdes))
