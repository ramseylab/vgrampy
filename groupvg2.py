import numpy as np
import vg2signal
import os
import sys
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for saving plots
import matplotlib.pyplot as plt
import io
from openpyxl.utils import get_column_letter

"""
make_xlsx_str
- creates parameter strings to save 'signal' and 'stats' files
- return: 'signal' and 'stats' filenames
"""


def make_xlsx_str(fn_ex, do_log, peak_feature):
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

    prfx = '_'.join(fn_ex.split('_')[0:4])+"_"+fn_ex.split('_')[4][:3]
    data_str = f'{log_str}{peak_str}_{prfx}.xlsx'

    return data_str

def save_df_excel(param_df, df, prfx, save_fn):
    def adjust_column(writer, sheet_name, df):
        ws = writer.sheets[sheet_name]
        for col_cells in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 2, 50)

    with pd.ExcelWriter(prfx+save_fn) as writer:
        df.to_excel(writer, sheet_name=prfx, index=False)
        adjust_column(writer, prfx, df)
        if prfx == 'signal':
            param_df.to_excel(writer, sheet_name='parameters')
            adjust_column(writer, 'parameters', param_df)




"""
run_vg2
- run vg2signal function from vg2signal.py
- save all peak signals into 'signals' file, save avg, std, cv, t-statistic in 'stats' file
- return: 
    vg_df: dictionary of potential, raw, log, smoothed, & detilted data
    data_str: string of parameters
- Added:
    - type_id: set analytes other than CBZ
    - v_start: voltage to start reading datafile, fix for other analytes not having the same data points
    - pv_min, and pv_max to adjust peak finding for other analyte locations
    - Allow csv data to be loaded for palmsense support
"""


def run_vg2(folderpath, do_log, peak_feature, smoothing_bw, stiffness, vwidth, type_id:str, v_start:str, pv_min, pv_max): # Add support for other analytes
    vg_dict = dict()
    dfxl = pd.DataFrame()
    os.chdir(folderpath)  # change to desired folderpath
    signal_lst = []
    conc_dict = dict()  # [analyte concentration]: peak signals
    all_param_df = pd.DataFrame()
    for filename in os.listdir():
        if filename[-3:] == 'txt' or filename[-3:] == 'csv': # Add support for .csv data
            print("Analyzing:", filename)
            (peak_signal, peak_v, vg_df, vcentershoulder, param_df) = vg2signal.v2signal(filename,
                                                                               do_log,
                                                                               peak_feature,
                                                                               smoothing_bw,
                                                                               vwidth,
                                                                               stiffness,
                                                                               v_start,
                                                                               pv_min,
                                                                               pv_max)
            all_param_df = pd.concat([all_param_df, param_df])
            idx1 = filename.rfind(type_id) # added support for non cbz analytes
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

            if peak_signal is None:  # if find no peak  # !!! why not N/A?
                peak_signal = 0
            if peak_v is None:      # !!! why not N/A?
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

    if do_log:        
        dfxl.columns = ["conc", "replicate", "V", "I", "logI", "smoothed", "detilted"]
    else:
        dfxl.columns = ["conc", "replicate", "V", "I", "smoothed", "detilted"]

    signal_df = pd.DataFrame(signal_lst, columns=["file", "signal", "peak V", "vcenter"])
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
    conc_df = pd.DataFrame(conc_lst_sorted, columns=["conc", "average", "std", "CV", "T-Statistic", "avg peak", "std peak"])

    # get filenames to save
    fn_ex = [fn for fn in os.listdir() if ('.txt' in fn) | ('.csv' in fn)][0]
    data_str = make_xlsx_str(fn_ex, do_log, peak_feature)
    save_df_excel(all_param_df, signal_df, "signal", data_str)
    save_df_excel(None, conc_df, "stats", data_str)
    save_df_excel(None, dfxl, "dataframe", data_str)

    return vg_dict, data_str.split('.xlsx')[0]





"""
plot_curtype(
    foldername: to save data, vg_df: df of data to plot, curtype: type of voltammogram,
    sep: separate by concentration (T), param_str: parameters to put in file string)
- plot voltammogram 
- save image to data folder
"""


def plot_curtype(foldername, vgdf, curtype, sep, param_str):
    fig, ax = plt.subplots(figsize=(4,3))
    colors = ['red', 'blue', 'green', 'black', 'pink']
    cnt = 0
    for conc in vgdf.keys():
        concstr = str(float(conc)) + " \u03BCM"
        vglst = vgdf[conc]
        for i in range(0, len(vglst)):
            vg = vglst[i]
            x = vg["V"]
            y = vg[curtype]
            if i == (len(vglst) - 1):
                ax.plot(x, y, color=colors[cnt], label=concstr)
            else:
                ax.plot(x, y, color=colors[cnt])
        cnt += 1
        ax.legend()
        if sep:
            ax.set_xlabel("Potential (V)")
            ax.set_title(f"{foldername} {curtype} voltammogram")
            if curtype == "smoothed":
                ax.set_ylabel("Current (i/\u03BCA)")
            else:
                ax.set_ylabel("Normalized Current")
            figname = curtype + "_" + concstr + param_str + ".png"
            plt.tight_layout()
            plt.savefig(figname)
            # plt.clf()
    if not sep:
        ax.set_title(f"{foldername} {curtype} voltammogram")
        ax.set_xlabel("Potential (V)")
        if curtype == "smoothed":
            ax.set_ylabel("Current (i/\u03BCA)")
        else:
            ax.set_ylabel("Normalized Current")
        figname = curtype + param_str + ".png"
        plt.tight_layout()
        plt.savefig(figname)
        # plt.clf()
        # plt.show()
    return fig, ax





"""
plot_vgrams(folderpath: folder to plot data from, vgdf: df of data to plot,
    sep: separate by concentration (T), param_str: parameters to put in file string)
- driver to plot both smoothed and detilted volgrammograms
- calls plot_curtype to plot and save
"""


def plot_vgrams(folderpath, vgdf, sep, param_str):  # alter for vg_d
    foldername = folderpath.split('/')[-1]
    smth_fig, smth_ax = plot_curtype(foldername, vgdf, "smoothed", sep, param_str)
    dtt_fig, dtt_ax = plot_curtype(foldername, vgdf, "detilted", sep, param_str)

    return smth_fig, smth_ax, dtt_fig, dtt_ax


"""
run_folderpath(folderpath: folder to run program)
- runs all combinations of parameters through the vg2signal.py functions
"""


def run_folderpath(path, user_input):
    folderpath=path
    toplot=user_input['toplot']
    sep=user_input['sep']
    do_log=user_input['do_log']
    peak_feat=user_input['peak_feat']
    smoothing_bw=user_input['smoothing_bw']
    stiffness=user_input['stiffness']
    vwidth=user_input['vwidth']
    type_id=user_input['type_id']
    v_start=user_input['v_start']
    pv_min=user_input['pv_min']
    pv_max=user_input['pv_max']

    vg_d, param_str = run_vg2(folderpath, do_log, peak_feat, smoothing_bw, stiffness, vwidth, type_id, v_start, pv_min, pv_max)

    if toplot:
        print("Saving Plots...")
        smth_fig, smth_ax, dtt_fig, dtt_ax = plot_vgrams(folderpath, vg_d, sep, param_str)
        print("Plots Saved")

        return smth_fig, smth_ax, dtt_fig, dtt_ax


if __name__ == '__main__': # added variables to maintain command line functionallity after other changes
    # folderpath to analyze
    sys.stdout = io.TextIOWrapper(open(sys.stdout.fileno(), 'wb', 0),
                                  write_through=True)  # StackOverflow:107705; see issue 4
    folder = input("Enter the path to analyze: ")
    if not os.path.exists(folder):
        sys.exit("Error: invalid file path")

    custom = input("Would you like to specify the analysis parameters (Y/N)?( Default: peak area, smoothing = "
                   "0.006, stiffness = 0, vwidth = 0.15, peak range = 1,1.1) ")

    if custom == "Y":
        do_loginput = bool(input("Do you want to log-transform? (1: log, 0: no log): "))

        peak_featinput = int(input("Enter the peak feature (curvature: 1, height: 2, area: 3): "))
        if peak_featinput < 1 or peak_featinput > 3:
            sys.exit("Error: invalid peak feature")

        smoothing_bwinput = float(input("Enter the smoothing parameter (>0): "))
        if smoothing_bwinput < 0:
            sys.exit("Error: invalid smoothing parameter")

        stiffnessinput = float(input("Enter the stiffness (>0): "))
        if stiffnessinput < 0:
            sys.exit("Error: invalid stiffness")

        vwidthinput = float(input("Enter the window width: "))
        vrange_list = input("Enter the area around the peak as <min>,<max>: ").split(",")
        pvmin = float(vrange_list[0])
        pvmax = float(vrange_list[1])
    else:
        do_loginput = True  # log param
        peak_featinput = 3 # 1:curvature, 2:height, 3:area
        smoothing_bwinput = 0.006  # smoothing bandwidth param
        stiffnessinput = 0  # stiffness param
        vwidthinput = 0.15  # detilt window width
        pv_min = 1
        pv_max = 1.1

    d_type_id = input("Enter the three letter code for your analyte: ")
    voltage_start = input("Enter the starting \'Potential\\V\' from your text files: ")

    plot = input("Would you like to plot? (Y/N): ")
    sepplot = False
    if plot == "Y":
        sepplot = input("Would you like to separate plots by concentration? (Y/N): ")
        if sepplot == "Y":
            sepplot = True
        else:
            sepplot = False
        plot = True
    else:
        plot = False

    # run vg2 for file
    print("Processing: " + folder)
    run_folderpath(folder, plot, sepplot, do_loginput, peak_featinput, smoothing_bwinput, stiffnessinput, vwidthinput, d_type_id, voltage_start, pv_min, pv_max)
