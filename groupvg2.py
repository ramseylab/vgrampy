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

if __name__ == '__main__':
    print("hey")
    folderpath = input("Folder to Process: ")
    if not os.path.exists(folderpath):
        sys.exit("Error: invalid file path")

    do_log = input("Log? (Y/N) ")
    if do_log == "Y":
        do_log = True
    elif do_log == "N":
        do_log = False
    else:
        sys.exit("Error: choose 'Y' or 'N'")

    recenter = input("Recenter? (Y/N) ")
    if recenter == "Y":
        recenter = True
    elif recenter == "N":
        recenter = False
    else:
        sys.exit("Error: choose 'Y' or 'N'")

    plot = input("Plot? (Y/N) ")
    if plot == "Y":
        plot = True
    elif plot == "N":
        plot = False
    else:
        sys.exit("Error: choose 'Y' or 'N'")
    smoothing_bw = float(input("Smoothing Bandwidth (default = 0.02) ") or 0.02)
    if smoothing_bw <= 0.0:
        sys.exit("Error: invalid bandwidth")
    smoothness_param = float(input("Smoothing Bandwidth (default = 0.0000001) ") or 0.0000001)
    if smoothness_param <= 0.0:
        sys.exit("Error: invalid smoothness")
    vcenter = float(input("Center (default = 1.073649114) ") or 1.073649114)
    vwidth = float(input("Width (default = 0.135) ") or 0.135)



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
        avgval = np.mean(val)
        stdval = np.std(val)
        cvval = stdval/avgval
        concstr = str(float(key))+"\u03BCM"
        conc_list.append([concstr,avgval,stdval,cvval])
    conc_df = pd.DataFrame(conc_list)
    #print(signal_df)
    conc_df.to_excel("stats.xlsx", index=False, header=["conc","average","std","CV"])
    signal_df.to_excel("signals.xlsx", index=False, header=["file", "signal"])