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
import xlsxwriter
import time

##make_xlsx_str
##creates parameter strings to save 'signal' and 'stats' files
##return: 'signal' and 'stats' filenames
def make_xlsx_str(do_log, recenter, smoothing_bw, stiffness, vcenter, vwidth1, vwidth2, logbase):
    if do_log == True:   #if run with log-transform
        log_str = "_log"+str(logbase)
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
def run_vg2(folderpath, do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth1, vwidth2, logbase):
    #get filenames to save
    #stats_str, signal_str = make_xlsx_str(do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth1, vwidth2, logbase)

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
                       stiffness_param,
                       logbase)
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
                       stiffness_param,
                       logbase)

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
    stats_str, signal_str = make_xlsx_str(do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth1, vwidth2, logbase)
    conc_df.to_excel(stats_str, index=False, header=["conc","average","std","CV","T-Statistic"])
    signal_df.to_excel(signal_str, index=False, header=["file", "signal","peak V"]) #save signal list to excel
    

def run_folderpath(folderpath, vcenter=1.073649114):
    if not os.path.exists(folderpath): #if folderpath does not exist
        sys.exit("Error: invalid file path") #exit

    do_log = True #log param
    recenter = True #double detilt/ recenter param
    #run_vg2(folderpath, do_log, recenter, smoothing_bw, stiffness_param, vcenter, vwidth)
    #change below to try different params
    logbase_lst = [2]
    bw_lst = [0.0001,0.000335,0.0000675,0.000125,0.00025,0.0005,0.001,0.0015,0.002,0.0025,0.003,0.0035]
    stiffness_lst = [0]
    vwidth1_lst = [0.12,0.125,0.13,0.135,0.14,0.145,0.15,0.155,0.16]
    vwidth2_lst = [0.12,0.125,0.13,0.135,0.14,0.145,0.15,0.155,0.16]
    vcenter_lst = [1.00]
    for s in stiffness_lst:
        print("stiffness=",s)
        #run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)
        for bw in bw_lst:
            print("bw=",bw)
            for w1 in vwidth1_lst:
                print("width1=",w1)
                for w2 in vwidth2_lst:
                    print("width2=",w2)
                    for c in vcenter_lst:
                        print("vcenter=",c)
                        for b in logbase_lst:
                            print("logbase=",b)
                            run_vg2(folderpath, do_log, recenter, bw, s, c, w1,w2,b)

def check_better_inner(bn,conc,filepath,pval,psignal,cvval,tsval):
    oldpval = bn[conc][1]
    oldpsignal = bn[conc][2]
    if oldpval > pval: #if this param val better than best
        bn[conc] = [filepath,pval,psignal,cvval,tsval] #reassign dict values (filepath, param value)
    elif oldpval == pval: #if param val the saem as best
        oldfn = bn[conc][0]
        #create list of filepaths to save in dict
        if type(oldfn) != list:
            oldfn = [oldfn, filepath]
        else:
            oldfn.append(filepath)
        bn[conc] = [oldfn,oldpval,oldpsignal, cvval, tsval]
    else:
        return False
    return bn

def check_better(b1, b2, b3, df, filepath, param):
    #print("in check better")
    #print("df: ", df)
    for i in range(len(df[param])): #for each concentration
        conc = df['conc'][i] #get concentration
        #print("conc: ", conc)
        cvval = df["CV"][i] #get parameter value (CV or T-Statistic)
        tsval = df["T-Statistic"][i] #get parameter value (CV or T-Statistic)
        pval = df[param][i]
        psignal = df['average'][i] #get average signal
        #filepath = folder+fn
        if conc in b1.keys(): #if conc already in dict
            b1n = check_better_inner(b1,conc,filepath,pval,psignal,cvval,tsval)
            if b1n == False:
                if conc in b2.keys():
                    b2n = check_better_inner(b2,conc,filepath,pval,psignal,cvval,tsval)
                    if b2n == False:
                        if conc in b3.keys():
                            b3n = check_better_inner(b3,conc,filepath,pval,psignal,cvval,tsval)
                            if b3n != False:
                                b3 = b3n                                
                        else:
                            b3[conc] = [filepath,pval,psignal,cvval,tsval]
                    else:
                        b2 = b2n
                else:
                    b2[conc] = [filepath,pval,psignal,cvval,tsval]
            else:
                b1 = b1n
        else: #if conc NOT in dict
            b1[conc] = [filepath,pval,psignal,cvval,tsval] #save initial path & param val
    return b1,b2,b3

def calc_rank(b, weight, r):
    for conc in b:
        fpn, pv, ps, cv, t = b[conc]
        if conc in r.keys():
            df = r[conc]
            cnt = weight
            #print(df)
            if type(fpn) == list:
                for fpnn in fpn:
                    if fpnn in df.index:
                        cnt = df.loc[fpn]["cnt"]
                        cnt += weight
                df.loc[fpnn] = [ps,cv,t,cnt]
            else:
                if fpn in df.index:
                    cnt = df.loc[fpn]["cnt"]
                    cnt += weight
                df.loc[fpn] = [ps,cv,t,cnt]
            
        else:
            data = ({"psignal": [ps],"CV": [cv], "T": [t], "cnt": [weight]})
            if type(fpn) == list:
                r[conc] = pd.DataFrame(data, index=[fpn[0]], columns = ["psignal","CV","T","cnt"])
            else:
                r[conc] = pd.DataFrame(data, index=[fpn], columns = ["psignal","CV","T","cnt"])
    return r

def get_best(folders, param):
    big_best= dict()
    big_best3 = dict()
    for folder in folders: #for each folder in list
        best1 = dict() #dictionary of best parameters
        best2 = dict() #dictionary of second best parameters
        best3 = dict() #dictionary of third best parameters
        best = dict()
        os.chdir(folder)
        
        for fn in os.listdir(): #for each 'stats' excel file in folder
            if fn[:5] == "stats":
                #print(fn)
                df = pd.read_excel(fn)
                filepath = folder+"_"+fn
                #print("File:", fn)
                best1, best2, best3 = check_better(best1, best2, best3, df, filepath, param)
                
                
        print("Best1: ", best1)
        print("Best2: ", best2)
        print("Best3: ", best3)     
        best1df = pd.DataFrame(data=best1)
        best1df.to_excel("best1.xlsx")
        best2df = pd.DataFrame(data=best2)
        best2df.to_excel("best2.xlsx")
        best3df = pd.DataFrame(data=best3)
        best3df.to_excel("best3.xlsx")
        ranked = dict() #dictionary of conc: Dataframe: index=fp: [cv, T, cnt]
        ranked = calc_rank(best1, 3, ranked)
        ranked = calc_rank(best2, 2, ranked)
        ranked = calc_rank(best3, 1, ranked)

        for conc in ranked:
            rconcdf = ranked[conc]
            fnb = rconcdf["cnt"].idxmax()
            #print(rconcdf)
            #print("BEST FN: ", fnb)
            #if type(fnb) == list:
                #fnb = fnb[0]
            #print(fnb)
            bestrow = rconcdf.loc[fnb]
            #print(bestrow)
            best[conc] = [fnb,bestrow[0], bestrow[1],bestrow[2]]
        big_best[folder] = best
        #bestdfall = pd.concat([best1df,best2df,best3df])
        #print(bestdfall)
        bestall = dict()
        for conc in best1.keys():
            lst1= best1[conc]
            lst2= best2[conc]
            lst3= best3[conc]
            alllst = [lst1,lst2,lst3]
            bestall[conc] = alllst
        #print(bestall)
        big_best3[folder] = bestall
    #return big_best
    return big_best3
   

def param_analysis(folders, param): #param-'CV' or 'T-Statistic'
    big_best = dict()
    for folder in folders: #for each folder in list
        best = dict() #dictionary of best parameters
        os.chdir(folder)
        
        for fn in os.listdir(): #for each 'stats' excel file in folder
            if fn[:5] == "stats":
                #print(fn)
                df = pd.read_excel(fn)
                for i in range(len(df[param])): #for each concentration
                    conc = df['conc'][i] #get concentration
                    cvval = df["CV"][i] #get parameter value (CV or T-Statistic)
                    tsval = df["T-Statistic"][i] #get parameter value (CV or T-Statistic)
                    pval = df[param][i]
                    psignal = df['average'][i] #get average signal
                    filepath = folder+"/"+fn
                    #print("OLD FILEPATH: ", filepath)
                    if conc in best.keys(): #if conc already in dict
                        oldpval = best[conc][1]
                        oldpsignal = best[conc][2]
                        if oldpval > pval: #if this param val better than best
                            best[conc] = [filepath,pval,psignal,cvval,tsval] #reassign dict values (filepath, param value)
                        elif oldpval == pval: #if param val the saem as best
                            oldfn = best[conc][0]
                            #create list of filepaths to save in dict
                            if type(oldfn) != list:
                                oldfn = [oldfn, filepath]
                            else:
                                oldfn.append(filepath)
                            best[conc] = [oldfn,oldpval,oldpsignal, cvval, tsval]
                    else: #if conc NOT in dict
                        best[conc] = [filepath,pval,psignal,cvval,tsval] #save initial path & param val
            big_best[folder]=best
        #print("Parameters for Best {}".format(param))
        #for key in best:
            #if key != "0.0\u03BCM":
            #print(key)
            #print(best[key]) 
    return big_best

def split_str(fn):
    folderfn = fn[fn.rfind("/")]
    fnsplit = fn.split("_")
    print(fnsplit)
    log = fnsplit[1]
    recenter = fnsplit[2]
    bw = fnsplit[3]
    stiff = fnsplit[4]
    vcenter = fnsplit[5]
    vwidth1 = fnsplit[6]
    #print(fnsplit[11])
    vwidth2 = fnsplit[7][:-5]
    foldern = fnsplit[0][:-5]
    return foldern, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2

def get_params(d):
    dfb = pd.DataFrame(columns=["conc",'avgsignal','CV','T-Statistic','log', 'recenter', 'bw','stiffness','vcenter','vwidth1','vwidth2'])
    #dfb = pd.DataFrame()
    for conc in d:
        #print(conc)
        #print(d[conc])
        fns, pval, psignal,cvval,tsval = d[conc]
        #fns, psignal, cvval,tsval = d[conc]
        print("GETPARAMS: ",fns)
        if type(fns) == str:
            foldern, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2 = split_str(fns)
        else:
            log = []
            recenter = []
            bw = []
            stiff = []
            vcenter = []
            vwidth1 = []
            vwidth2 = []
            for fn in fns:
                foldernn, logn, recentern, bwn, stiffn, vcentern, vwidth1n, vwidth2n = split_str(fn)
                log.append(logn)
                recenter.append(recentern)
                bw.append(bwn)
                stiff.append(stiffn)
                vcenter.append(vcentern)
                vwidth1.append(vwidth1n)
                vwidth2.append(vwidth2n)
            foldern = foldernn
        dfb.loc[len(dfb.index)] = [conc, psignal, cvval, tsval,  log, recenter, bw, stiff, vcenter, vwidth1, vwidth2]
    dfb.columns = [foldern,'avgsignal','CV','T-Statistic','log', 'recenter', 'bw','stiffness','vcenter','vwidth1','vwidth2']
    return dfb


def condense_best(folderss, fbest,param):
    os.chdir(folderss[0])
    os.chdir("..")
    cwd = os.getcwd()
    start = 0
    excel_path = os.path.join(cwd, "best_stats.xlsx")
    for fn in fbest:
        f= fbest[fn]
        #print("F IN FBEST:",f)
        dfn = get_params(f)
        if not os.path.exists(excel_path):
            dfn.to_excel(excel_path, sheet_name="Sheet1", index=False, engine='openpyxl')
        else:
            with pd.ExcelWriter(excel_path, engine='openpyxl', if_sheet_exists='overlay', mode='a') as writer: 
                dfn.to_excel(writer,sheet_name="Sheet1",index=False,startrow=writer.sheets["Sheet1"].max_row,startcol=0)

def condense_best3(folderss, fbest,param):
    os.chdir(folderss[0])
    os.chdir("..")
    cwd = os.getcwd()
    start = 0
    excel_path = os.path.join(cwd, "best_stats.xlsx")
    for bestn in fbest:
        f= fbest[fn]
        print("BestN; ", bestn)
        dfn = get_params(f)
        if not os.path.exists(excel_path):
            dfn.to_excel(excel_path, sheet_name="Sheet1", index=False, engine='openpyxl')
        else:
            with pd.ExcelWriter(excel_path, engine='openpyxl', if_sheet_exists='overlay', mode='a') as writer: 
                dfn.to_excel(writer,sheet_name="Sheet1",index=False,startrow=writer.sheets["Sheet1"].max_row,startcol=0)

if __name__ == '__main__':
    start_time = time.time()
    #folderpath to analyze
    #foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_08/2023_06_16_Large2']
    #stats_log_recenter_0.004_1e-22_1.073649114_0.135
    #foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/0',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/0p05',
               # 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/0p075',
               # 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/0p1',
              #  'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/0p25',
               # 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/0p5']
    foldersS = ['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/2023_06_16_Large2', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/2023_06_19_Large3',
                'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/2023_04_19_SOD4',
               'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/today/2023_04_03_SOD2/S4',
              ]
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
        bd=param_analysis(foldersS,'CV')
        #bd = get_best(foldersS,'CV')
        #condense_best3(foldersS, bd, 'CV')
        condense_best(foldersS, bd, 'CV')
        sys.exit()

    #run vg2 for each file in each folder in list SALIVA
    for folder in foldersS:
        print("Processing: "+folder)
        run_folderpath(folder)

    #analyze for best parameters
    bd=param_analysis(foldersS,'CV')
    #bd = get_best(foldersS,'CV')
    condense_best(foldersS, bd, 'CV')
    totaltime = time.time()-start_time
    print("Total Time: ",totaltime)