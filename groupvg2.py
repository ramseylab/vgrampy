import numpy as np
import pandas
import scipy.interpolate
import typing
import argparse
import numpy
import skfda.misc.hat_matrix as skfda_hm
import skfda.preprocessing.smoothing as skfda_smoothing
import skfda
import csaps
import matplotlib.pyplot as plt
import vg2signal
import os
import sys
import pandas as pd
from statistics import mean
import openpyxl

def run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth):
    if log_str == True:   
        log_str = "_log"
    else:
        log_str = "_NOlog"
    if recenter_str == True:
        recenter_str = "_recenter"
    else:
        recenter_str "_NOrecenter"
    
    smoothing_str = "_"+str(smoothing_bw)
    smoothness_str = "_"+str(smoothness_param)
    vcenter_str = "_"+str(vcenter)
    vwidth_str = "_"+str(vwidth)
    data_str = log_str+recenter_str+smoothing_str+smoothness_str+vcenter_str+vwidth_str+".xlsx"
    stats_str = "stats"+data_str
    signal_str = "signal"+data_str

    os.chdir(folderpath)
    signal_lst = []
    conc_dict = dict()
    #signal_lst = pd.DataFrame()
    for filename in os.listdir():
        if filename[-3:] == 'txt':
            (peak_signal, peak_v, vg_df) = vg2signal.v2signal(filename,
                       do_log,
                       smoothing_bw,
                       vcenter,
                       vwidth,
                       smoothness_param)
            print(filename)
            #print(f"Signal: {peak_signal:0.3f} 1/V^2")
            idx1 = filename.rfind("cbz")
            idx2 = filename[idx1:].find("_")
            conc = filename[idx1+3:idx1+idx2]
            if 'p' in conc:
                pi = conc.find('p')
                conctemp = conc[:pi]+'.'+conc[pi+1:]
                conc = conctemp
            #print(conc)
            if peak_signal == None:
                    peak_signal = 0
            signal_lst.append([filename, peak_signal])
            if conc in conc_dict.keys():
                conclst = conc_dict[conc]
                conclst.append(peak_signal)
                conc_dict[conc] = conclst
            else:
                
                conc_dict[conc] = [peak_signal]
            #print(f"Signal: {peak_signal:0.3f} 1/V^2")
    signal_df = pd.DataFrame(signal_lst)
    conc_list = []
    for key in conc_dict:
        #print(key)
        val = conc_dict[key]
        #print(conc_dict[key])
        print(val)
        avgval = np.average(val)
        stdval = np.std(val)
        cvval = stdval/avgval
        concstr = str(float(key))+"\u03BCM"
        conc_list.append([concstr,avgval,stdval,cvval])
    conc_df = pd.DataFrame(conc_list)
    #print(signal_df)
    #stats_title = "stats_"+ 
    conc_df.to_excel(stats_str, index=False, header=["conc","average","std","CV"])
    signal_df.to_excel(signal_str, index=False, header=["file", "signal"])

def param_analysis(folderpath):
    print("param_analysis")
    

if __name__ == '__main__':
    
    folderpath = input("Folder to Process: ")
    analysis = input("Aggregate Analyze? (Y/N): ")
    if not os.path.exists(folderpath):
        sys.exit("Error: invalid file path")

    do_log = False
    #log_str = "_log"
    recenter = True
    recenter_str = "_recenter"
    plot = False
    smoothing_bw = 0.00000001
    smoothing_str = "_"+str(smoothing_bw)
    smoothness_param = 0.00000001
    smoothness_str = "_"+str(smoothness_param)
    vcenter = 1.073649114
    vwidth = 0.135

    param_lst = [0.00000001,0.0000001,0.03,0.000000000000000000000000000000000001]
    #smoothness_param_lst = [0.0000001, 0.00000001,0.000000001,0.0000000001]
    #vwidth_param_lst = [0.148, 0.150]
    for s in param_lst:
        run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)

    if analysis == "Y":
        param_analysis(folderpath)