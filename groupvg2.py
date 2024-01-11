import numpy as np
import vg2signal
import os
import sys
import pandas as pd
import scipy.stats as stats
import time


##make_xlsx_str
##creates parameter strings to save 'signal' and 'stats' files
##return: 'signal' and 'stats' filenames
def make_xlsx_str(do_log, recenter, smoothing_bw, stiffness, vcenter, vwidth1, vwidth2):
    if do_log == True:  # if run with log-transform
        log_str = "_log"
    else:  # if not use log-transform
        log_str = "_NOlog"
    if recenter == True:  # if run with double detilt/ recentering
        recenter_str = "_recenter"
    else:  # if not recentering
        recenter_str = "_NOrecenter"

    smoothing_str = "_" + str(smoothing_bw)
    stiffness_str = "_" + str(stiffness)
    vcenter_str = "_" + str(vcenter)
    vwidth1_str = "_" + str(vwidth1)
    vwidth2_str = "_" + str(vwidth2)
    # combine all params into one string
    data_str = log_str + recenter_str + smoothing_str + stiffness_str + vcenter_str + vwidth1_str + vwidth2_str + ".xlsx"
    return data_str


##run vg2 function from vg2signal.py
##run through each text file in folder
##save all peak signals into 'signals' file, save avg, std, cv, t-statistic in 'stats' file
def run_vg2(folderpath, do_log, recenter, smoothing_bw, stiffness, vcenter, vwidth1, vwidth2):
    # get filenames to save
    data_str = make_xlsx_str(do_log, recenter, smoothing_bw, stiffness, vcenter, vwidth1, vwidth2)
    vg_dict = dict()
    dfxl = pd.DataFrame()
    os.chdir(folderpath)  # change to desired folderpath
    signal_lst = []
    conc_dict = dict()  # [cbz concentration]: peak signals
    for filename in os.listdir():
        if filename[-3:] == 'txt':
            print("Analyzing:", filename)
            (peak_signal, peak_v, vg_df, vcentershoulder, ph) = vg2signal.v2signal(filename,
                                                                                   do_log,
                                                                                   smoothing_bw,
                                                                                   vcenter,
                                                                                   vwidth1,
                                                                                   stiffness)

            idx1 = filename.rfind("cbz")
            idx2 = filename[idx1:].find("_")
            conc = filename[idx1 + 3:idx1 + idx2]
            replicate = filename[idx1 + idx2 + 1:filename.rfind(".")]

            if 'p' in conc:  # for 7p5 concentration
                pi = conc.find('p')
                conctemp = conc[:pi] + '.' + conc[pi + 1:]
                conc = conctemp
            concstrxl = str(float(conc))
            concxl = list([concstrxl] * len(vg_df["V"]))
            replicatexl = list([replicate] * len(vg_df["V"]))
            if do_log:
                dfxl = pd.concat([dfxl, pd.DataFrame(
                    [concxl, replicatexl, vg_df["V"], vg_df["I"], vg_df["logI"], vg_df["smoothed"],
                     vg_df["detilted"]]).transpose()])
            else:
                dfxl = pd.concat([dfxl, pd.DataFrame(
                    [concxl, replicatexl, vg_df["V"], vg_df["I"], vg_df["smoothed"], vg_df["detilted"]]).transpose()])

            if peak_signal == None:  # if find no peak
                peak_signal = 0
            if peak_v == None:
                peak_v = 0
            signal_lst.append([filename, round(peak_signal, 2), round(peak_v, 3), round(vcentershoulder, 3),
                               ph])  # add text filename & peak signal to signal list
            if conc in conc_dict.keys():  # for each concentration
                conclst = conc_dict[conc]
                conclst.append((peak_signal, peak_v))  # add peak signal to concentration dictionary
                conc_dict[conc] = conclst

                # for plotting purposes
                plst = vg_dict[conc]
                plst.append(vg_df)
                vg_dict[conc] = plst
            else:
                conc_dict[conc] = [(peak_signal, peak_v)]
                vg_dict[conc] = [vg_df]

    signal_df = pd.DataFrame(signal_lst)
    conc_list = []
    for key in conc_dict:  # for each concentration
        vals = conc_dict[key]  # all the signals for conc
        avgval = round(np.average([val[0] for val in vals]), 2)  # avg signal for conc
        stdval = round(np.std([val[0] for val in vals]), 2)  # std of signals for conc
        avgpeakval = round(np.average([val[1] for val in vals]), 2)  # avg peak voltage for conc
        stdpeakval = round(np.std([val[1] for val in vals]), 2)  # std of peak voltage for conc
        if avgval != 0:
            cvval = round(stdval / avgval, 3)
        else:
            cvval = 0  # if average is 0, make CV 0
        concstr = str(float(key)) + " \u03BCM"
        # compare signal list for this conc to no cbz
        if "00" in conc_dict.keys():
            zerolst = conc_dict["00"]
            ttest = round(stats.ttest_ind([val[0] for val in vals], [val[0] for val in zerolst])[0], 2)
        else:
            ttest = 0
        conc_list.append([concstr, avgval, stdval, cvval, ttest, avgpeakval, stdpeakval])  # add stats for conc

    conc_lst_sorted = sorted(conc_list, key=lambda x: float(x[0][:-2]))
    conc_df = pd.DataFrame(conc_lst_sorted)
    # save stats list to excel
    stats_str = "stats" + data_str
    signal_str = "signal" + data_str
    dataframe_str = "dataframe" + data_str
    conc_df.to_excel(stats_str, index=False,
                     header=["conc", "average", "std", "CV", "T-Statistic", "avg peak", "std peak"])
    signal_df.to_excel(signal_str, index=False,
                       header=["file", "signal", "peak V", "vcenter", "PH"])  # save signal list to excel
    if do_log:
        dfxl.to_excel(dataframe_str, index=False,
                      header=["conc", "replicate", "V", "I", "logI", "smoothed", "detilted"])
    else:
        dfxl.to_excel(dataframe_str, index=False, header=["conc", "replicate", "V", "I", "smoothed", "detilted"])
    return vg_dict, data_str


def run_folderpath(folderpath):
    if not os.path.exists(folderpath):  # if folderpath does not exist
        sys.exit("Error: invalid file path")  # exit

    do_log = False  # log param
    recenter = False  # double detilt/ recenter param
    # change below to try different params
    logbase_lst = [2]
    bw_lst = [0.006]#np.arange(0.0001,0.01,0.0001)
    stiffness_lst = np.arange(0,0.001,0.00005)
    vwidth1_lst = [0.15] #np.arange(0.13,0.20,0.001)#[0.12, 0.125, 0.13, 0.135, 0.14, 0.145, 0.15, 0.155, 0.16]
    vwidth2_lst = [0.17]  # np.arange(0.13,0.18,0.001)
    vcenter_lst = [1.04]  # np.arange(1.00,1.08,0.005)
    for s in stiffness_lst:
        print("stiffness=", s)
        # run_vg2(folderpath, do_log, recenter, smoothing_bw, s, vcenter, vwidth)
        for bw in bw_lst:
            print("bw=", bw)
            for w1 in vwidth1_lst:
                print("width1=", w1)
                for w2 in vwidth2_lst:
                    print("width2=", w2)
                    for c in vcenter_lst:
                        print("vcenter=", c)
                        run_vg2(folderpath, do_log, recenter, bw, s, c, w1, w2)


def param_analysis(folders, param):  # param-'CV' or 'T-Statistic'
    big_best = dict()
    for folder in folders:  # for each folder in list
        best = dict()  # dictionary of best parameters
        os.chdir(folder)

        for fn in os.listdir():  # for each 'stats' excel file in folder
            if fn[:5] == "stats":
                print(fn)
                df = pd.read_excel(fn)
                for i in range(len(df[param])):  # for each concentration
                    conc = df['conc'][i]  # get concentration
                    cvval = df["CV"][i]  # get parameter value (CV or T-Statistic)
                    tsval = df["T-Statistic"][i]  # get parameter value (CV or T-Statistic)
                    pval = df[param][i]
                    psignal = df['average'][i]  # get average signal
                    filepath = folder + "/" + fn

                    if conc in best.keys():  # if conc already in dict
                        oldpval = best[conc][1]
                        oldpsignal = best[conc][2]
                        if oldpval > pval and pval != 0:  # if this param val better than best
                            best[conc] = [filepath, pval, psignal, cvval,
                                          tsval]  # reassign dict values (filepath, param value)
                        elif oldpval == pval:  # if param val the saem as best
                            oldfn = best[conc][0]
                            # create list of filepaths to save in dict
                            if type(oldfn) != list:
                                oldfn = [oldfn, filepath]
                            else:
                                oldfn.append(filepath)
                            best[conc] = [oldfn, oldpval, oldpsignal, cvval, tsval]
                    else:  # if conc NOT in dict
                        best[conc] = [filepath, pval, psignal, cvval, tsval]  # save initial path & param val
            big_best[folder] = best
    return big_best


def split_str(fn):
    fnsplit = fn.split("_")
    # print(fnsplit[-3])
    log = fnsplit[-7]
    recenter = fnsplit[-6]
    bw = fnsplit[-5]
    stiff = fnsplit[-4]
    vcenter = fnsplit[-3]
    vwidth1 = fnsplit[-2]
    vwidth2 = fnsplit[-1][:-5]
    foldern = fnsplit[-8][:-5]
    return foldern, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2


def get_params(d):
    dfb = pd.DataFrame(
        columns=["conc", 'avgsignal', 'CV', 'T-Statistic', 'log', 'recenter', 'bw', 'stiffness', 'vcenter', 'vwidth1',
                 'vwidth2'])
    for conc in d:
        fns, pval, psignal, cvval, tsval = d[conc]
        print("GETPARAMS: ", fns)
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
        dfb.loc[len(dfb.index)] = [conc, psignal, cvval, tsval, log, recenter, bw, stiff, vcenter, vwidth1, vwidth2]
    dfb.columns = [foldern, 'avgsignal', 'CV', 'T-Statistic', 'log', 'recenter', 'bw', 'stiffness', 'vcenter',
                   'vwidth1', 'vwidth2']
    return dfb


def condense_best(folderss, fbest, param):
    os.chdir(folderss[0])
    os.chdir("..")
    cwd = os.getcwd()
    start = 0
    excel_path = os.path.join(cwd, "best_stats.xlsx")
    for fn in fbest:
        f = fbest[fn]
        dfn = get_params(f)
        if not os.path.exists(excel_path):
            dfn.to_excel(excel_path, sheet_name="Sheet1", index=False, engine='openpyxl')
        else:
            with pd.ExcelWriter(excel_path, engine='openpyxl', if_sheet_exists='overlay', mode='a') as writer:
                dfn.to_excel(writer, sheet_name="Sheet1", index=False, startrow=writer.sheets["Sheet1"].max_row,
                             startcol=0)


if __name__ == '__main__':
    start_time = time.time()
    folders = [
               'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/manuscript2/nolog/LC3/2023_12_12_LowConc3',
               ]
    just_analysis = "N"
    if just_analysis == "Y":
        bd = param_analysis(folders, 'CV')
        condense_best(folders, bd, 'CV')
        sys.exit()

    # run vg2 for each file in each folder in list SALIVA
    for folder in folders:
        print("Processing: " + folder)
        run_folderpath(folder)

    # analyze for best parameters
    bd = param_analysis(folders, 'CV')
    condense_best(folders, bd, 'CV')
    totaltime = time.time() - start_time
    print("Total Time: ", totaltime)
