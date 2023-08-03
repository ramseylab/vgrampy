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
def make_xlsx_str(do_log, recenter, smoothing_bw, stiffness, vcenter, vwidth1, vwidth2):
    if do_log == True:   #if run with log-transform
        log_str = "_log"
    else: #if not use log-transform
        log_str = "_NOlog"
    if recenter == True: #if run with double detilt/ recentering
        recenter_str = "_recenter"
    else: #if not recentering
        recenter_str = "_NOrecenter"
    
    smoothing_str = "_"+str(smoothing_bw)
    stiffness_str = "_"+str(stiffness)
    vcenter_str = "_"+str(vcenter)
    vwidth1_str = "_"+str(vwidth1)
    vwidth2_str = "_"+str(vwidth2)
    #combine all params into one string
    data_str = log_str+recenter_str+smoothing_str+stiffness_str+vcenter_str+vwidth1_str+vwidth2_str+".xlsx"
    stats_return = "stats"+data_str
    signal_return = "signal"+data_str
    return stats_return, signal_return

def new_vwidth(vgdf):
    v = vgdf["V"]
    d = vgdf["detilted"]
    no0first = next((i for i, j in enumerate(d) if j),None)
    dr = reversed(d)
    no0last = next((i for i, j in enumerate(dr) if j),None)
    v1 = v[no0first]
    v2 = v[len(d)-no0last-1]
    vwnew = v2-v1
    vcnew = v1+vwnew/2
    return vcnew, vwnew

##run vg2 function from vg2signal.py
##run through each text file in folder
##save all peak signals into 'signals' file, save avg, std, cv, t-statistic in 'stats' file
def run_vg2(folderpath, do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth1, vwidth2):
    #get filenames to save
    stats_str, signal_str = make_xlsx_str(do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth1, vwidth2)

    os.chdir(folderpath) #change to desired folderpath
    signal_lst = []
    conc_dict = dict() #[cbz concentration]: peak signals
    for filename in os.listdir():
        if filename[-3:] == 'txt':
            print("Analyzing: ", filename)
            (peak_signal, peak_v, vg_df) = vg2signal.v2signal(filename,
                       do_log,
                       smoothing_bw,
                       vcenter,
                       vwidth1,
                       stiffness_param)
            if recenter:
                vcenter2= peak_v
                if vcenter2 == None:
                    vcenter2 = vcenter
                #vcenter2, vwidth2 = new_vwidth(vg_df)
                (peak_signal, peak_v, vg_df) = vg2signal.v2signal(filename,
                       do_log,
                       smoothing_bw,
                       vcenter2,
                       vwidth2,
                       stiffness_param)
            print(list(vg_df["V"]))
            print(list(vg_df["detilted"]))
            idx1 = filename.rfind("cbz")
            idx2 = filename[idx1:].find("_")
            conc = filename[idx1+3:idx1+idx2]
            if 'p' in conc: #for 7p5 concentration
                pi = conc.find('p')
                conctemp = conc[:pi]+'.'+conc[pi+1:]
                conc = conctemp
            
            if peak_signal == None: #if find no peak
                peak_signal = 0
            #add text filename & peak signal to signal list
            if peak_v == None:
                peak_v = 0
            signal_lst.append([filename, round(peak_signal,2), round(peak_v,3)])
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
        avgval = round(np.average(val),2) #avg signal for conc
        stdval = round(np.std(val),2) #std of signals for conc
        if avgval != 0:
            cvval = round(stdval/avgval,3)
        else:
            cvval = 0 #if average is 0, make CV 0
        concstr = str(float(key))+"\u03BCM"
        #compare signal list for this conc to no cbz
        if "00" in conc_dict.keys():
            zerolst = conc_dict["00"]
            ttest = round(stats.ttest_ind(val,zerolst)[0],2)
        else:
            ttest = 0
        conc_list.append([concstr,avgval,stdval,cvval,ttest]) #add stats for conc

    conc_lst_sorted = sorted(conc_list, key=lambda x:float(x[0][:-2]))
    conc_df = pd.DataFrame(conc_lst_sorted)
    #save stats list to excel
    conc_df.to_excel(stats_str, index=False, header=["conc","average","std","CV","T-Statistic"])
    signal_df.to_excel(signal_str, index=False, header=["file", "signal","peak V"]) #save signal list to excel
    

def run_folderpath(folderpath, vcenter=1.073649114):
    if not os.path.exists(folderpath): #if folderpath does not exist
        sys.exit("Error: invalid file path") #exit

    do_log = True #log param
    recenter = True #double detilt/ recenter param
    smoothing_bw = 0.02 #smoothing bandwidth param
    stiffness_param = 0.00000001 #stiffness param
    #vcenter = 1.073649114 #center for detilt window
    vwidth = 0.135 #detilt window width
    #run_vg2(folderpath, do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth)
    #change below to try different params
    bw_lst = [0.004]
    stiffness_lst = [0]
    vwidth1_lst = [0.16]
    vwidth2_lst = [0.155999]
    vcenter_lst = [1.073649114]
    for s in stiffness_lst:
        print("stiffness=",s)
        #run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)
        for bw in bw_lst:
            print("bw=",s)
            for w1 in vwidth1_lst:
                print("width1=",w1)
                for w2 in vwidth2_lst:
                    print("width2=",w2)
                    for c in vcenter_lst:
                        print("vcenter=",c)
                        run_vg2(folderpath, do_log, recenter, bw, s, c, w1,w2)
    

def param_analysis(folders, param): #param-'CV' or 'T-Statistic'
    big_best = dict()
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
                    pval = df[param][i] #get parameter value (CV or T-Statistic)
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
        #best_df = pd.DataFrame(best)

        #best_df = best_df.T
        #best_df.to_excel("best_stats.xlsx", index=False, header=["file", param, "Average Signal"])
        #print("Parameters for Best {}".format(param))
        #for key in best:
            #if key != "0.0\u03BCM":
                #print(key)
                #print(best[key])
        big_best[folder]=best
    return big_best
    #print("Parameters for Best {}".format(param))
    #for key in best:
        #print(key)
        #print(best[key])

def split_str(fn):
    fnsplit = fn.split("_")
    #print(fnsplit)
    log = fnsplit[5]
    recenter = fnsplit[6]
    bw = fnsplit[7]
    stiff = fnsplit[8]
    vcenter = fnsplit[9]
    vwidth1 = fnsplit[10]
    vwidth2 = fnsplit[11][:-5]
    foldern = fnsplit[4][:-5]
    print(foldern)
    return foldern, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2

def get_params(d):
    #fpsplit = fp.split("_")
    print("in get params")
    for conc in d:
        print(conc)
        print(d[conc])
        fns, pval, psignal = d[conc]
        if type(fns) == str:
            foldern, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2 = split_str(fns)
        else:
            for fn in fns:
                foldern, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2 = split_str(fn)
                
        

def condense_best(folderss, fbest,param):
    #fbest_df = pd.DataFrame(best)
    for fn in fbest:
        f= fbest[fn]
        get_params(f)


    #best_df.to_excel("best_stats.xlsx", index=False, header=["file", param, "Average Signal"])

if __name__ == '__main__':
    #folderpath to analyze
    foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_03/2023_04_19_SOD4']
    #stats_log_recenter_0.004_1e-22_1.073649114_0.135
    #foldersS = ['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_06_16_Large2', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_06_19_Large3',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_19_SOD4',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S4',
               #]
    #foldersS = ['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_09_SAL1/N','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_09_SAL1/SAL',]
    #foldersS =[#'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_19_SOD4',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_02/2023_04_03_SOD2/S4',
               #]# 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_17_SAL2/N','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_17_SAL2/SAL',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p2)onN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)onN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)pN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p2)pN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)inSnoN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)inS',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_06_29_KNonWorking1/S1','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_06_29_KNonWorking1/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_06_29_KNonWorking1/S3',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_07_14_KNonWorking2/S1','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_07_14_KNonWorking2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_07_14_KNonWorking2/S3']
    #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_09_SAL1/N','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_09_SAL2/SAL',
                #foldersB =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_08_Buffer1/ph6txt',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_08_Buffer1/ph7txt',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_08_Buffer1/ph8txt',
              # 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_12_Buffer2/1',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_12_Buffer2/2',
               #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_26_firstvwidth/2023_06_12_Buffer2/3']
    #just_analysis = input("Just param_analysis? (Y/N) ")
    just_analysis = "N"
    if just_analysis == "Y":
        bd=param_analysis(foldersS,'T-Statistic')
        #condense_best(foldersS, bd, 'T-Statistic')
        sys.exit()

    #run vg2 for each file in each folder in list SALIVA
    for folder in foldersS:
        print("Processing: "+folder)
        run_folderpath(folder)

    #analyze for best parameters
    param_analysis(foldersS,'T-Statistic')