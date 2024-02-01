import numpy as np
import vg2signal
import os
import sys
import pandas as pd
import scipy.stats as stats
import time

"""
make_xlsx_str
- creates parameter strings to save 'signal' and 'stats' files
- return: 'signal' and 'stats' filenames
"""


def make_xlsx_str(do_log, peak_feature, smoothing_bw, stiffness, vwidth):
    if do_log:  # if run with log-transform
        log_str = "_log"
    else:  # if not use log-transform
        log_str = "_NOlog"
    if peak_feature == 1:
        peak_str = "_curvature"
    elif peak_feature == 2:
        peak_str = "_height"
    else:
        peak_str = "_area"

    smooth_str = "_" + str(smoothing_bw)
    stiff_str = "_" + str(stiffness)
    vwidth_str = "_" + str(vwidth)
    # combine all params into one string
    data_str = log_str + peak_str + smooth_str + stiff_str + vwidth_str + ".xlsx"
    return data_str


"""
run_vg2
- run vg2signal function from vg2signal.py
- save all peak signals into 'signals' file, save avg, std, cv, t-statistic in 'stats' file
- return: 
    vg_df: dictionary of potential, raw, log, smoothed, & detilted data
    data_str: string of parameters
"""


def run_vg2(folderpath, do_log, peak_feature, smoothing_bw, stiffness, vwidth):
    # get filenames to save
    data_str = make_xlsx_str(do_log, peak_feature, smoothing_bw, stiffness, vwidth)
    vg_dict = dict()
    dfxl = pd.DataFrame()
    os.chdir(folderpath)  # change to desired folderpath
    signal_lst = []
    conc_dict = dict()  # [cbz concentration]: peak signals
    for filename in os.listdir():
        if filename[-3:] == 'txt':
            print("Analyzing:", filename)
            (peak_signal, peak_v, vg_df, vcentershoulder) = vg2signal.v2signal(filename,
                                                                               do_log,
                                                                               peak_feature,
                                                                               smoothing_bw,
                                                                               vwidth,
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

            if peak_signal is None:  # if find no peak
                peak_signal = 0
            if peak_v is None:
                peak_v = 0
            # add text filename & peak signal to signal list
            signal_lst.append([filename, round(peak_signal, 4), round(peak_v, 3), round(vcentershoulder, 3)])
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
    concs_targetlst = sorted([c for idx, c in enumerate(list(conc_dict.keys()))], key=lambda v: float(v))

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
        # compare signal list for this conc to closest lower conc
        currentidx = concs_targetlst.index(key)
        if currentidx == 0:
            lowervals = conc_dict[key]
        else:
            lowervals = conc_dict[concs_targetlst[currentidx-1]]
        ttest = round(stats.ttest_ind([val[0] for val in vals], [val[0] for val in lowervals], equal_var=False)[0], 2)
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
                       header=["file", "signal", "peak V", "vcenter"])  # save signal list to excel
    if do_log:
        dfxl.to_excel(dataframe_str, index=False,
                      header=["conc", "replicate", "V", "I", "logI", "smoothed", "detilted"])
    else:
        dfxl.to_excel(dataframe_str, index=False, header=["conc", "replicate", "V", "I", "smoothed", "detilted"])
    return vg_dict, data_str


"""
run_folderpath(folderpath: folder to run program)
- runs all combinations of parameters through the vg2signal.py functions
"""


def run_folderpath(folderpath):
    if not os.path.exists(folderpath):  # if folderpath does not exist
        sys.exit("Error: invalid file path")  # exit

    do_log = True  # log param
    p_f = 1  # 1:curvature, 2:height, 3:area
    # change below to try different params
    smoothing_lst = [0.006]
    stiffness_lst = [0]  # np.arange(0, 0.001, 0.001)
    vwidth_lst = [0.15]  # np.arange(0.13,0.20,0.01)
    for stiffness in stiffness_lst:
        print("stiffness=", stiffness)
        for smoothing in smoothing_lst:
            print("bw=", smoothing)
            for vwidth in vwidth_lst:
                print("vwidth=", vwidth)
                run_vg2(folderpath, do_log, p_f, smoothing, stiffness, vwidth)


"""
param_analysis(foldersanalysis: folders to analyze, param: parameter to determine 'best'
- compares each combination of parameters based on 'param'
- returns best combination of parameters, & their statistics
"""


def param_analysis(foldersanalysis, param):  # param-'CV' or 'T-Statistic'
    big_best = dict()
    for folderi in foldersanalysis:  # for each folder in list
        best = dict()  # dictionary of best parameters
        os.chdir(folderi)

        for fn in os.listdir():  # for each 'stats' excel file in folder
            if fn[:5] == "stats":
                df = pd.read_excel(fn)
                for i in range(len(df[param])):  # for each concentration
                    conc = df['conc'][i]  # get concentration
                    cvval = df["CV"][i]  # get parameter value (CV or T-Statistic)
                    tsval = df["T-Statistic"][i]  # get parameter value (CV or T-Statistic)
                    pval = df[param][i]
                    psignal = df['average'][i]  # get average signal
                    filepath = folderi + "/" + fn

                    if conc in best.keys():  # if conc already in dict
                        oldpval = best[conc][1]
                        oldpsignal = best[conc][2]
                        if oldpval > pval != 0:  # if this param val better than best
                            best[conc] = [filepath, pval, psignal, cvval,
                                          tsval]  # reassign dict values (filepath, param value)
                        elif oldpval == pval:  # if param val the saem as best
                            oldfn = best[conc][0]
                            # create list of filepaths to save in dict
                            if not isinstance(oldfn, list):
                                oldfn = [oldfn, filepath]
                            else:
                                oldfn.append(filepath)
                            best[conc] = [oldfn, oldpval, oldpsignal, cvval, tsval]
                    else:  # if conc NOT in dict
                        best[conc] = [filepath, pval, psignal, cvval, tsval]  # save initial path & param val
            big_best[folderi] = best
    return big_best


"""
split_str(fn: file name to split)
returns: folder name, and parameters split up
"""


def split_str(fn):
    fnsplit = fn.split("_")
    log = fnsplit[-5]
    pf = fnsplit[-4]
    bw = fnsplit[-3]
    stiff = fnsplit[-2]
    vwidth = fnsplit[-1][:-5]
    foldern = fnsplit[-8][:-5]
    return foldern, log, pf, bw, stiff, vwidth


"""
get_params(d: dataframe)
- get data for best parameters
- return: dataframe for best parameters for each concentration
"""


def get_params(d):
    dfb = pd.DataFrame(
        columns=["conc", 'avgsignal', 'CV', 'T-Statistic', 'log', 'peakfeature', 'bw', 'stiffness', 'vwidth'])
    foldern = None
    foldernn = None
    for conc in d:
        fns, pval, psignal, cvval, tsval = d[conc]
        if isinstance(fns, str):
            foldern, log, pf, bw, stiff, vwidth = split_str(fns)
        else:
            log = []
            bw = []
            pf = []
            stiff = []
            vwidth = []
            for fn in fns:
                foldernn, logn, pfn, bwn, stiffn, vwidthn = split_str(fn)
                log.append(logn)
                pf.append(pfn)
                bw.append(bwn)
                stiff.append(stiffn)
                vwidth.append(vwidthn)
            foldern = foldernn
        dfb.loc[len(dfb.index)] = [conc, psignal, cvval, tsval, log, pf, bw, stiff, vwidth]
    dfb.columns = [foldern, 'avgsignal', 'CV', 'T-Statistic', 'log', 'peakfeature', 'bw', 'stiffness', 'vwidth']
    return dfb


"""
condense_best(folderss: folder to analyze subfolders, fbest: dataframe of best parameters)
- writes best parameters & their statistics to an excel file
"""


def condense_best(folderss, fbest):
    os.chdir(folderss[0])
    os.chdir("..")
    cwd = os.getcwd()
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
        'C:/Users/temp/Box/Fu Lab/Noel/CBZdata/cleancode/2023_12_12_LowConc3',
        'C:/Users/temp/Box/Fu Lab/Noel/CBZdata/cleancode/2023_12_15_LowConc4',
        'C:/Users/temp/Box/Fu Lab/Noel/CBZdata/cleancode/2023_12_17_LowConc5',
    ]
    just_analysis = "N"
    if just_analysis == "Y":
        bd = param_analysis(folders, 'CV')
        condense_best(folders, bd)
        sys.exit()

    # run vg2 for each file in each folder in list
    for folder in folders:
        print("Processing: " + folder)
        run_folderpath(folder)

    # analyze for best parameters
    bd = param_analysis(folders, 'CV')
    condense_best(folders, bd)
    totaltime = time.time() - start_time
    print("Total Time: ", totaltime)
