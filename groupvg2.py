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
import scipy.stats as stats

##make_xlsx_str
##creates parameter strings to save 'signal' and 'stats' files
##return: 'signal' and 'stats' filenames
def make_xlsx_str(do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth):
    if do_log == True:   #if run with log-transform
        log_str = "_log"
    else: #if not use log-transform
        log_str = "_NOlog"
    if recenter == True: #if run with double detilt/ recentering
        recenter_str = "_recenter"
    else: #if not recentering
        recenter_str = "_NOrecenter"
    
    smoothing_str = "_"+str(smoothing_bw)
    smoothness_str = "_"+str(smoothness_param)
    vcenter_str = "_"+str(vcenter)
    vwidth_str = "_"+str(vwidth)
    #combine all params into one string
    data_str = log_str+recenter_str+smoothing_str+smoothness_str+vcenter_str+vwidth_str+".xlsx"
    stats_return = "stats"+data_str
    signal_return = "signal"+data_str
    return stats_return, signal_return

##run vg2 function from vg2signal.py
##run through each text file in folder
##save all peak signals into 'signals' file, save avg, std, cv, t-test in 'stats' file
def run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth):
    #get filenames to save
    stats_str, signal_str = make_xlsx_str(do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth)

    os.chdir(folderpath) #change to desired folderpath
    signal_lst = []
    conc_dict = dict() #[cbz concentration]: peak signals
    for filename in os.listdir():
        if filename[-3:] == 'txt':
            (peak_signal, peak_v, vg_df) = vg2signal.v2signal(filename,
                       do_log,
                       smoothing_bw,
                       vcenter,
                       vwidth,
                       smoothness_param)
            if recenter:
                vwidth2 = 0.15
                vcenter2= peak_v
                if type(vcenter2) != float:
                    vcenter2 = 0.135
                (peak_signal, peak_v, vg_df) = vg2signal.v2signal(filename,
                       do_log,
                       smoothing_bw,
                       vcenter,
                       vwidth2,
                       smoothness_param)
            print(filename)
            idx1 = filename.rfind("cbz")
            idx2 = filename[idx1:].find("_")
            conc = filename[idx1+3:idx1+idx2]
            if 'p' in conc: #for 7p5 concentration
                pi = conc.find('p')
                conctemp = conc[:pi]+'.'+conc[pi+1:]
                conc = conctemp
            
            if peak_signal == None: #if find no peak
                peak_signal = 0
            signal_lst.append([filename, peak_signal, peak_v]) #add text filename & peak signal to signal list
            if conc in conc_dict.keys(): #for each concentration
                conclst = conc_dict[conc]
                conclst.append(peak_signal) #add peak signal to concentration dictionary
                conc_dict[conc] = conclst
            else:
                conc_dict[conc] = [peak_signal]

    signal_df = pd.DataFrame(signal_lst)
    conc_list = []
    for key in conc_dict: #for each concentration
        val = conc_dict[key] #all the signals for conc
        avgval = np.average(val) #avg signal for conc
        stdval = np.std(val) #std of signals for conc
        if avgval != 0:
            cvval = stdval/avgval
        else:
            cvval = 0 #if average is 0, make CV 0
        concstr = str(float(key))+"\u03BCM"
        #compare signal list for this conc to no cbz
        if "00" in conc_dict.keys():
            zerolst = conc_dict["00"]
            ttest = stats.ttest_ind(val,zerolst)[0]
        else:
            ttest = 0
        conc_list.append([concstr,avgval,stdval,cvval,ttest]) #add stats for conc

    conc_lst_sorted = sorted(conc_list, key=lambda x:float(x[0][:-2]))
    conc_df = pd.DataFrame(conc_lst_sorted)
    #save stats list to excel
    conc_df.to_excel(stats_str, index=False, header=["conc","average","std","CV","T-Test"])
    signal_df.to_excel(signal_str, index=False, header=["file", "signal","peak V"]) #save signal list to excel
    

def run_folderpath(folderpath, vcenter=1.073649114):
    if not os.path.exists(folderpath): #if folderpath does not exist
        sys.exit("Error: invalid file path") #exit

    do_log = True #log param
    recenter = True #double detilt/ recenter param
    smoothing_bw = 0.02 #smoothing bandwidth param
    smoothness_param = 0.00000001 #smoothness param
    #vcenter = 1.073649114 #center for detilt window
    vwidth = 0.135 #detilt window width
    #run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth)
    #change below to try different params
    bw_lst = [0.003]
    smoothness_lst = [0.0000000000000000000001, 0, 0.00000001,0.0000001]
    vwidth_lst = [0.15]
    vcenter_lst = [1.073649114]
    for s in smoothness_lst:
        print("smoothness=",s)
        #run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)
        for bw in bw_lst:
            print("bw=",s)
            #run_vg2(folderpath, do_log, recenter, bw, s, vcenter, vwidth)
            for w in vwidth_lst:
                print("width=",w)
                #run_vg2(folderpath, do_log, recenter, bw, s, vcenter, w)
                for c in vcenter_lst:
                    print("vcenter=",c)
                    run_vg2(folderpath, do_log, recenter, bw, s, c, w)
    

def param_analysis(folders, param): #param-'CV' or 'T-Test'
    
    for folder in folders: #for each folder in list
        best = dict() #dictionary of best parameters
        os.chdir(folder)
        #print(folder)
        for fn in os.listdir(): #for each 'stats' excel file in folder
            if fn[:5] == "stats":
                #print(fn)
                df = pd.read_excel(fn)
                for i in range(len(df[param])): #for each concentration
                    conc = df['conc'][i] #get concentration
                    pval = df[param][i] #get parameter value (CV or t-Test)
                    psignal = df['average'][i] #get average signal
                    filepath = folder+fn
                    if conc in best.keys(): #if conc already in dict
                        oldpval = best[conc][1]
                        oldpsignal = best[conc][2]
                        if oldpval > pval: #if this param val better than best
                            best[conc] = [filepath,pval,psignal] #reassign dict values (filepath, param value)
                        elif oldpval == pval: #if param val the saem as best
                            oldfn = best[conc][0]
                            #create list of filepaths to save in dict
                            if type(oldfn) != list:
                                oldfn = [oldfn, filepath]
                            else:
                                oldfn.append(filepath)
                            best[conc] = [oldfn,oldpval,oldpsignal]
                    else: #if conc NOT in dict
                        best[conc] = [filepath,pval,psignal] #save initial path & param val
        print("Parameters for Best {}".format(param))
        for key in best:
            print(key)
            print(best[key])
    print("Parameters for Best {}".format(param))
    for key in best:
        print(key)
        print(best[key])


if __name__ == '__main__':
    #folderpath to analyze
    #stats_log_recenter_0.004_1e-22_1.073649114_0.135
    foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_19_SOD4',
                'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S4']
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_27/2023_05_17_SAL2/N','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_27/2023_05_17_SAL2/SAL',
    #foldersB =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_08_Buffer1/ph6txt',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_08_Buffer1/ph7txt',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_08_Buffer1/ph8txt',
              # 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_12_Buffer2/1',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_12_Buffer2/2',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_12_Buffer2/3']
    #just_analysis = input("Just param_analysis? (Y/N) ")
    just_analysis = "N"
    if just_analysis == "Y":
        param_analysis(foldersS,'CV')
        sys.exit()

    #run vg2 for each file in each folder in list SALIVA
    for folder in foldersS:
        print("Processing: "+folder)
        run_folderpath(folder)

    #analyze for best parameters
    param_analysis(foldersS,'CV')