#!/usr/bin/env python3

import os, sys, glob, re
import argparse
import numpy as np
import pandas as pd
import shutil
import networkx as nx
import matplotlib.pyplot as plt

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Checking temporal and spatial baseline for pair selection')
    parser.add_argument('-d','--directory', type=str, required=True, help='directory for processing', dest='dir')
    parser.add_argument('-i','--input', type=str, required=True, help='input file for baseline estimation', dest='input')
    parser.add_argument('-l','--ifg', type=str, required=True, help='list of interferograms', dest='ifg')
    parser.add_argument('-o','--output', type=str, required=True, help='output file for date pairs', dest='output')
    parser.add_argument('-s','--scene', type=str, required=True, help='file containing list of scenes/images', dest='scene')
    parser.add_argument('-t','--temp', type=float, required=True, help='temporal baseline threshold', dest='temp')
    parser.add_argument('-p','--perp', type=float, required=True, help='perpendicular baseline threshold', dest='perp')
    parser.add_argument('-a','--date', type=str, required=True, help='dateID info file for scene reference', dest='date')
    arg = parser.parse_args()
    
    return arg


def GetDateID(datefile):
    '''
    Args:
        datefile:  dateID.info 

    Returns:
        date_list: orbID    date    original_name
    '''
    date_list = []
    file = open(datefile)
    for line in file:
        date = line.split('\n')[0]
        date_list.append(date.split())
    return date_list


def get_scenes_position(rootdir,filexml,dateID):
    date_list = GetDateID(dateID)
    scene_ref = date_list[0][1]

    # Read isceproc.xml and calculate baselines
    data = [[scene_ref,0]]
    df_ifg = pd.DataFrame(data,columns=['Scenes','RelativeHeight'])

    fx = open(rootdir+'/'+filexml,'r')
    orf = fx.readlines()
    with open(rootdir+'/'+filexml) as f:  
        line = f.readline()
        cnt = 1
        while line:
            match = re.search(r'.perp_baseline_bottom', line.strip(), re.DOTALL)
            if match:
                perp_bsln = float(re.findall("[-+]?\d*\.\d+|[-+]?\d+", line.strip())[0])
                # Get the dateinfo at 9th line before the current one.
                dateinfo = orf[cnt-9]
                datepair = re.findall(r"[-+]?\d*\.\d+|\d+", dateinfo)

                # Estimate relative positions
                if datepair[0]==scene_ref:
                    data = [[datepair[1],perp_bsln]]
                    df = pd.DataFrame(data,columns=['Scenes','RelativeHeight'])
                    df_ifg = df_ifg.append(df, ignore_index=True)               
            line = f.readline()
            cnt += 1
    return df_ifg


def baseline_check(Graph,rootdir,filexml,temp_thres,perp_thres,dateID):
    """
    Check the temporal and spatial baseline of each pair
    Write satisfied pairs to output for isceApp.xml
    """
    # Identify reference scene (first scene)
    date_list = GetDateID(dateID)

    fx = open(rootdir+'/'+filexml,'r')
    orf = fx.readlines()
    with open(rootdir+'/'+filexml) as f:  
        line = f.readline()
        cnt = 1
        while line:
            match = re.search(r'.perp_baseline_bottom', line.strip(), re.DOTALL)
            if match:
                perp_bsln = float(re.findall("[-+]?\d*\.\d+|[-+]?\d+", line.strip())[0])
                
                # Get the dateinfo at 9th line before the current one.
                dateinfo = orf[cnt-9]
                datepair = re.findall(r"[-+]?\d*\.\d+|\d+", dateinfo)
                
                # Convert to pandas format
                date_master = pd.to_datetime(datepair[0])
                date_slave = pd.to_datetime(datepair[1])
                temp_bsln = (date_slave-date_master)/np.timedelta64(1, 'D')

                # Check baseline conditions
                if temp_bsln<temp_thres and np.abs(perp_bsln)<perp_thres:
                    # print("Pair: {} & {}, temp: {} (days), perp:{} (m)".format(date_master.date(), date_slave.date(), temp_bsln, perp_bsln))                    
                    Graph.add_edge(datepair[0],datepair[1],perpbsln=perp_bsln)                        
            line = f.readline()
            cnt += 1


# This function optimizes the network of interferograms.
# The aim is to ensure degree of connectivity at each nodes
# but the minimize the number of edges among nodes.
def optimize_pairs(G,scenes,heights,i,temp_thres,perp_thres):
    scenes2 = [x for j,x in enumerate(scenes) if (j!=i)]
    heights2 = [x for j,x in enumerate(heights) if (j!=i)]
    
    temp = 50       # days
    perp = 100      # meter

    d = G.degree(scenes[i])
    iter = 0
    while (d < 4) and (iter<1000):
        for j in range (0,len(scenes2)):
            perp_bsln = heights2[j] - heights[i]
            date_master = pd.to_datetime(scenes[i])
            date_slave = pd.to_datetime(scenes2[j])
            temp_bsln = (date_slave-date_master)/np.timedelta64(1, 'D')
            if (temp_bsln<temp) and (np.abs(perp_bsln)<perp):
                G.add_edge(scenes[i],scenes2[j],perpbsln=perp_bsln)
            else:
                temp = temp + (iter%2) * temp*0.05
                if temp > temp_thres:
                    temp = temp_thres
                perp = perp + (iter+1)%2 * perp*0.05
                if perp > perp_thres:
                    perp = perp_thres
            d = G.degree(scenes[i])
        iter+=1


if __name__ == '__main__':    
    if len(sys.argv) < 16:
        print('Number of arguments: %d \n' % len(sys.argv))
        print('Error in Baseline_ALOS_checking.py: Number of arguments is not matched!')
        sys.exit()
    else:
        args = cmdLineParse()
        rootdir = args.dir
        infile = args.input
        ifglist = args.ifg
        outfile = args.output
        scenefile = args.scene
        temp_thres = args.temp
        perp_thres = args.perp
        dateID = args.date

    # If previous datepair file exist, remove it.
    if os.path.exists(outfile):
        os.remove(outfile)

    # Get Scene names and heights
    df_ifg = get_scenes_position(rootdir,infile,dateID)
    df_ifg.to_csv('Baseline_table.csv', index=False)

    scenes = df_ifg['Scenes']
    heights = df_ifg['RelativeHeight']
    num_scene = df_ifg.shape[0]
    
    G = nx.Graph()
    for i in range(0,num_scene):
        node = str(int(scenes[i]))
        date = float(node[0:4]) + (float(node[4:6])-1)/12. + (float(node[6:8])-1)/365.
        G.add_node(node,pos=(date,heights[i]))

    # Adding egdes satisfying thresholds
    baseline_check(G,rootdir,infile,50,100,dateID)

    # Optimize interferogram network
    for i in range(0,num_scene):
        optimize_pairs(G,scenes,heights,i,temp_thres,perp_thres)

    print("Number of pairs: "+str(G.number_of_edges()) +"\n")
    # Write scenes used to file
    fsce = open(scenefile,"w")
    for i in range(0,num_scene):
        if G.degree(scenes[i]) > 0:
            fsce.write(scenes[i] + '\n')
    fsce.close()

    # Write pair info to file
    fout = open(outfile,"w")
    fifg = open(ifglist,"w")
    pairinfo = G.edges(data=True)
    for i,v in enumerate(pairinfo):
        fout.write(v[0]+'__'+v[1]+'\n')
        perp_bsln = list(v[2].values())
        fifg.write(v[0]+'\t'+v[1]+'\t'+str(perp_bsln[0])+'\t'+'ALOS \n')
    fout.close()
    fifg.close()
        
    plt.figure(figsize=(12,6))
    pos=nx.get_node_attributes(G,'pos')
    nx.draw_networkx_nodes(G, pos, node_size=30, node_color="red", with_labels=False)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    plt.xlabel('Date Acquisition')
    plt.ylabel('Perp. Baseline')
    med = np.median(heights)
    plt.gca().set_ylim([med-2000,med+2000])
    dirpath = os.getcwd()
    foldername = os.path.basename(dirpath)
    plt.savefig(foldername + '.png')
    plt.savefig('../' + foldername + '.png')
