import pandas as pd
import matplotlib.pyplot as plt
import os
import vg2signal
import sys


def get_data(folderdata, trend, statdata):
    os.chdir(folderdata)  # change directory to folder to get data
    if statdata == 1:  # if desired statistic is CV
        statstr = "CV"
    else:  # if desired statistic is T-Statistic
        statstr = "T-Statistic"
    gdict = dict()
    for fn in os.listdir():  # for each 'stats' excel file in folder
        if fn[:5] == "stats":
            # param to trend
            paramval = float(fn[:-5].split('_')[trend + 2])
            df = pd.read_excel(fn)
            for i in range(len(df[statstr])):  # for each concentration
                conc = df['conc'][i]  # get concentration
                statval = df[statstr][i]  # get stat value (CV or T-Statistic)
                # for each concentration
                if conc in gdict.keys():
                    prevtrends = gdict[conc][0]
                    prevstat = gdict[conc][1]
                    prevtrends.append(paramval)
                    prevstat.append(statval)
                    gdict[conc][0] = prevtrends
                    gdict[conc][1] = prevstat
                else:
                    gdict[conc] = [[paramval], [statval]]
    return gdict


def plot_trend(pltn, folderplot, trend, statplot, zerosplot):
    gdict = get_data(folderplot, trend, statplot)
    colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']  # colors to plot different concs
    shapes = ['o', 's', 'v', 'X']  # shapes to plot different concs
    cnt = 0
    ax1 = pltn
    # sort concentrations to lowest to highest
    concs_targetlst = sorted([c for idx, c in enumerate(list(gdict.keys()))], key=lambda v: float(v[:-3]))
    for key in gdict:  # for each concentration
        if ((key == "0.0 \u03BCM") and zerosplot) or (key != "0.0 \u03BCM"):
            if statplot == 2:  # if stat is t-statistic
                currentidx = concs_targetlst.index(key)
                prevval = concs_targetlst[currentidx - 1]
                labelname = key + " & " + prevval + " samples"
                ax1.scatter(gdict[key][0], gdict[key][1], label=labelname, color=colors[cnt], facecolors='none',
                            marker=shapes[cnt])
            else:
                ax1.scatter(gdict[key][0], gdict[key][1], label=key, color=colors[cnt], marker=shapes[cnt])
        cnt += 1

    if stat == 1:  # if stat is CV
        ax1.set_ylim(0, 0.90)
        ax1.set_ylabel("signal CV", weight='bold', fontsize=15)
    else:  # if stat is t-statistic
        ax1.set_ylim(-1, 20)
        ax1.set_ylabel("t-statistic", weight='bold', fontsize=15)
    if trend == 1:  # if trend is smoothing
        ax1.set_xlabel('smoothing', weight='bold', fontsize=15)
    elif trend == 2:  # if trend is stiffness
        ax1.set_xscale('log')
        ax1.set_xlabel('stiffness', weight='bold', fontsize=15)
    elif trend == 3:  # if trend is window width
        ax1.set_xlabel('window width', weight='bold', fontsize=15)
    ax1.legend(prop={'size': 13})


def plot_double_trend(pltn, folderdouble, trend, zerosdouble):
    xlabels = ["smoothing_bw", "stiffness", "vcenter", "vwidth1", "vwidth2"]
    dictcv = get_data(folderdouble, trend, 'CV')
    dicttt = get_data(folderdouble, trend, 'T-Statistic')
    ax1 = pltn

    colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']
    shapes = ['o', 's', 'v', 'h', 'X']
    cnt = 0
    concs_targetlst = sorted([c for idx, c in enumerate(list(dictcv.keys()))], key=lambda v: float(v[:-3]))
    for key in dictcv:
        currentidx = concs_targetlst.index(key)
        prevval = concs_targetlst[currentidx - 1]
        labelname = key + " & " + prevval + " samples"
        if (key == "0.0 \u03BCM" and zerosdouble) or key != "0.0 \u03BCM":
            ax1.scatter(dictcv[key][0], dictcv[key][1], label=key + ' CV', marker=shapes[cnt],
                        edgecolors=colors[cnt])
        cnt += 1
    ax1.tick_params(axis='y')
    ax1.set_xlabel(xlabels[trend - 1])
    ax1.set_ylabel('CV')
    ax1.set_ylim(0, 0.90)
    ax2 = ax1.twinx()
    cnt = 0
    for key in dicttt:
        if key != "0.0 \u03BCM":
            ax2.scatter(dicttt[key][0], dicttt[key][1], label=key + ' T-Statistic', marker=shapes[cnt],
                        facecolors='none', color=colors[cnt])
        cnt += 1
    ax2.tick_params(axis='y')
    ax2.set_ylabel('T-Statistic')
    ax2.set_ylim(-1, 20)
    if trend == 1:  # if trend is smoothing
        ax1.set_xlabel('smoothing', weight='bold', fontsize=15)
    elif trend == 2:  # if trend is stiffness
        ax1.set_xscale('log')
        ax1.set_xlabel('stiffness', weight='bold', fontsize=15)
    elif trend == 3:  # if trend is window width
        ax1.set_xlabel('window width', weight='bold', fontsize=15)
    ax1.legend(prop={'size': 7})
    ax2.legend(prop={'size': 7})
    #pltn.suptitle(titlename)


def plotraw(folders):
    colors = ['tab:orange', 'tab:blue', 'tab:green', 'tab:red', 'tab:purple']
    cnt = 0
    for folderraw in folders:
        os.chdir(folderraw)
        for fn in os.listdir():  # for each 'stats' excel file in folder
            if fn[-3:] == "txt":
                underlines = fn.split("_")
                cbzamt = underlines[-2][-2:]
                print(cbzamt)
                if cbzamt == "15":
                    print("in")
                    vgdf = vg2signal.read_raw_vg_as_df(str(fn))
                    plt.plot(vgdf["V"], vgdf["I"], color=colors[cnt])
        cnt += 1
    plt.title("Raw Voltammogram")
    plt.xlabel("Potential (V)")
    plt.ylabel("Current (\u03BCM)")
    plt.show()


if __name__ == '__main__':
    foldersS = ['C:/Users/temp/Box/Fu Lab/Noel/CBZdata/cleancode/2023_12_12_LowConc3',
                ]
    tall = 0
    wide = 0
    param1 = 1  # 1=smoothing_bw,2=stiffness,3=vwidth
    param2 = 5
    stat = 3  # 1:'CV' or 2:'T-Statistic' or 3:both
    zeros = False
    groupraw = False
    if groupraw:
        plotraw(foldersS)
        sys.exit()
    fig, axs = plt.subplots()
    for folder in foldersS:
        if stat != 3:

            plot_trend(axs, folder, param1, stat, zeros)
        else:
            plot_double_trend(axs, folder, param1, zeros)
    plt.show()
