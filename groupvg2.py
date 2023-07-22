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
            signal_lst.append([filename, peak_signal]) #add text filename & peak signal to signal list
            if conc in conc_dict.keys(): #for each concentration
                conclst = conc_dict[conc]
                conclst.append(peak_signal) #add peak signal to concentration dictionary
                conc_dict[conc] = conclst
            else:
                conc_dict[conc] = [peak_signal]

    signal_df = pd.DataFrame(signal_lst)
    conc_list = []
    for key in conc_dict: #for each concentration
        #print(key)
        val = conc_dict[key] #all the signals for conc
        avgval = np.average(val) #avg signal for conc
        stdval = np.std(val) #std of signals for conc
        if avgval != 0:
            cvval = stdval/avgval
        else:
            cvval = 0 #if average is 0, make CV 0
        concstr = str(float(key))+"\u03BCM"
        #compare signal list for this conc to no cbz
        zerolst = conc_dict["00"]
        ttest = stats.ttest_ind(zerolst,val)[1]
        conc_list.append([concstr,avgval,stdval,cvval,ttest]) #add stats for conc

    conc_df = pd.DataFrame(conc_list)
    #save stats list to excel
    conc_df.to_excel(stats_str, index=False, header=["conc","average","std","CV","T-Test"])
    signal_df.to_excel(signal_str, index=False, header=["file", "signal"]) #save signal list to excel
    

def run_folderpath(folderpath):
    if not os.path.exists(folderpath): #if folderpath does not exist
        sys.exit("Error: invalid file path") #exit

    do_log = True #log param
    recenter = True #double detilt/ recenter param
    smoothing_bw = 0.02 #smoothing bandwidth param
    smoothness_param = 0.00000001 #smoothness param
    vcenter = 1.073649114 #center for detilt window
    vwidth = 0.135 #detilt window width
    run_vg2(folderpath, do_log, recenter, smoothing_bw, smoothness_param, vcenter, vwidth)
    #change below to try different params

def param_analysis(folders, param): #param-'CV' or 'T-Test'
    best = dict() #dictionary of best parameters
    for folder in folders: #for each folder in list
        os.chdir(folder)
        #print(folder)
        for fn in os.listdir(): #for each 'stats' excel file in folder
            if fn[:5] == "stats":
                #print(fn)
                df = pd.read_excel(fn)
                for i in range(len(df[param])): #for each concentration
                    conc = df['conc'][i] #get concentration
                    pval = df[param][i] #get parameter value (CV or t-Test)
                    filepath = folder+fn
                    if conc in best.keys(): #if conc already in dict
                        oldpval = best[conc][1]
                        if oldpval > pval: #if this param val better than best
                            best[conc] = (filepath,pval) #reassign dict values (filepath, param value)
                        elif oldpval == pval: #if param val the saem as best
                            oldfn = best[conc][0]
                            #create list of filepaths to save in dict
                            if type(oldfn) != list:
                                oldfn = [oldfn, filepath]
                            else:
                                oldfn.append(filepath)
                            best[conc] = (oldfn,oldpval)
                    else: #if conc NOT in dict
                        best[conc] = (filepath,pval) #save initial path & param val
    print("Parameters for Best {}".format(param))
    for key in best:
        print(key)
        print(best[key])


if __name__ == '__main__':
    #folderpath to analyze
    folders =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_06_08_Buffer1/ph6txt',
                'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_06_08_Buffer1/ph7txt',
                'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_06_08_Buffer1/ph8txt',
                'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_04_19_SOD4',
                'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/k3/sg/2023_04_03_SOD2/S4']

    #just_analysis = input("Just param_analysis? (Y/N) ")
    just_analysis = "N"
    if just_analysis == "Y":
        param_analysis(folders,'T-Test')
        sys.exit()

    #run vg2 for each file in each folder in list
    for folder in folders:
        print("Processing: "+folder)
        run_folderpath(folder)

    #analyze for best parameters
    param_analysis(folders,'T-Test')