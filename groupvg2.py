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

def make_xlsx_str(do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth):
    if do_log == True:   
        log_str = "_log"
    else:
        log_str = "_NOlog"
    if recenter == True:
        recenter_str = "_recenter"
    else:
        recenter_str = "_NOrecenter"
    
    smoothing_str = "_"+str(smoothing_bw)
    smoothness_str = "_"+str(smoothness_param)
    vcenter_str = "_"+str(vcenter)
    vwidth_str = "_"+str(vwidth)
    data_str = log_str+recenter_str+smoothing_str+smoothness_str+vcenter_str+vwidth_str+".xlsx"
    stats_return = "stats"+data_str
    signal_return = "signal"+data_str
    return stats_return, signal_return


def run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth):
    stats_str, signal_str = make_xlsx_str(do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth)

    os.chdir(folderpath)
    signal_lst = []
    conc_dict = dict()
    for filename in os.listdir():
        if filename[-3:] == 'txt':
            (peak_signal, peak_v, vg_df) = vg2signal.v2signal(filename,
                       do_log,
                       smoothing_bw,
                       vcenter,
                       vwidth,
                       smoothness_param)
            #print(filename)
            idx1 = filename.rfind("cbz")
            idx2 = filename[idx1:].find("_")
            conc = filename[idx1+3:idx1+idx2]
            if 'p' in conc:
                pi = conc.find('p')
                conctemp = conc[:pi]+'.'+conc[pi+1:]
                conc = conctemp
            
            if peak_signal == None:
                    peak_signal = 0
            signal_lst.append([filename, peak_signal])
            if conc in conc_dict.keys():
                conclst = conc_dict[conc]
                conclst.append(peak_signal)
                conc_dict[conc] = conclst
            else:
                
                conc_dict[conc] = [peak_signal]

    signal_df = pd.DataFrame(signal_lst)
    conc_list = []
    for key in conc_dict:
        val = conc_dict[key]
        avgval = np.average(val)
        stdval = np.std(val)
        if avgval != 0:
            cvval = stdval/avgval
        else:
            cvval = 0
        concstr = str(float(key))+"\u03BCM"
        conc_list.append([concstr,avgval,stdval,cvval])

    conc_df = pd.DataFrame(conc_list)
    conc_df.to_excel(stats_str, index=False, header=["conc","average","std","CV"])
    signal_df.to_excel(signal_str, index=False, header=["file", "signal"])
    

def run_folderpath(folderpath):
    if not os.path.exists(folderpath):
        sys.exit("Error: invalid file path")

    do_log = False
    recenter = True
    smoothing_bw = 0.00000001
    smoothness_param = 0.00000001
    vcenter = 1.073649114
    vwidth = 0.135

    param_lst = [0.00000001,0.0000001,0.03,0.000000000000000000000000000000000001]
    vwidth_param_lst = [0.125,0.133,0.135,0.145]
    for s in param_lst:
        print(s)
        run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)
        for s in param_lst:
            print(s)
            run_vg2(folderpath, do_log, recenter, s, smoothness_param, vcenter, vwidth)
            for s in vwidth_param_lst:
                print(s)
                run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, s)

    do_log = True
    for s in param_lst:
        print(s)
        run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)
        for s in param_lst:
            print(s)
            run_vg2(folderpath, do_log, recenter, s, smoothness_param, vcenter, vwidth)
            for s in vwidth_param_lst:
                print(s)
                run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, s)


def param_analysis(folders):
    best = dict()
    for folder in folders:
        os.chdir(folder)
        print(folder)
        for fn in os.listdir():
            if fn[:5] == "stats":
                print(fn)
                df = pd.read_excel(fn)
                for i in range(len(df['CV'])):
                    conc = df['conc'][i]
                    cv = df['CV'][i]
                    if conc in best.keys():
                        oldcv = best[conc][1]
                        if oldcv > cv:
                            print("better")
                            best[conc] = (fn,cv)
                        elif oldcv == cv:
                            print("same")
                            oldfn = best[conc][0]
                            if type(oldfn) != list:
                                oldfn = [oldfn, fn]
                            else:
                                oldfn.append(fn)
                            best[conc] = (oldfn,oldcv)
                    else:
                        best[conc] = (fn,cv)
    for key in best:
        print(key)
        print(best[key])


if __name__ == '__main__':
    folders =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/multiplefolders/2023_04_19_SOD4'] #['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/multiplefolders/2023_06_08_Buffer1/ph6txt',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/multiplefolders/2023_06_08_Buffer1/ph7txt',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/multiplefolders/2023_06_08_Buffer1/ph8txt']
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/multiplefolders/2023_04_19_SOD4']
    for folder in folders:
        print("Processing: "+folder)
        run_folderpath(folder)

    param_analysis(folders)