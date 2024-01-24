import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import sys
import pandas as pd

"""
plotraw(filename, labels)
"""


def plot_raw(filename, labels, colorslst):
    if filename[-3:] == 'txt':
        print("plotting file:", filename)
        fp = open(filename, 'r')
        xs = []
        ys = []
        idx1 = filename.rfind("cbz")
        idx2 = filename[idx1:].find("_")
        conc = filename[idx1 + 3:idx1 + idx2]

        if 'p' in conc:  # for 7p5 concentration
            pi = conc.find('p')
            conctemp = conc[:pi] + '.' + conc[pi + 1:]
            conc = conctemp
        conc_str = str(float(conc))+" \u03BCM"
        for line in fp:
            if line[0].isnumeric():
                potential, diff, f, rev = line.split(',')
                potential = float(potential)
                current = -float(diff) * 1000000
                xs.append(potential)
                ys.append(current)
        labelkeys = list(labels.keys())
        if conc_str in labelkeys:
            plt.plot(xs, ys, color=labels[conc_str])
        else:
            newcolor = colorslst.pop()
            plt.plot(xs, ys, color=newcolor, label=conc_str)
            labels[conc_str] = newcolor
    return labels

def makedicts(file, ytype):
    df = pd.read_excel(file)
    dicttype = dict()
    concs = set((l[0], l[1]) for l in df.values)
    for c, d in concs:
        x = [l[2] for l in df.values if l[0] == c and l[1] == d]
        if ytype == "R":
            y = [l[3] for l in df.values if l[0] == c and l[1] == d]
        elif ytype == "L":
            y = [l[4] for l in df.values if l[0] == c and l[1] == d]
        elif ytype == "S":
            y = [l[4] for l in df.values if l[0] == c and l[1] == d]
        else:
            y = [l[5] for l in df.values if l[0] == c and l[1] == d]

        dicttype[(c, d)] = (x, y)
    return dicttype

def plotdataframe(datadf):
    colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']  # colors to plot different concs
    for key, val in datadf.items():
        plt.plot(val[0], val[1], label=key, colors=colors.pop())

if __name__ == '__main__':
    multiple = input("Would you like to plot one (O) or multiple (M) voltammograms?: ")
    if multiple != "O" and multiple != "M":
        print("Invalid input, enter (O) or (M)")
        sys.exit()

    filetype = input("Do you have a Dataframe file (D) or text (T)?: ")
    if filetype == "D":
        vgramtype = input("Would you like to plot raw (R), log (L), smoothed (S), detilted (D), or all (A) voltammograms?: ")
    else:
        vgramtype = "raw"
    fig, ax = plt.subplots()
    if vgramtype == "raw":
        if multiple == "O":
            fn = input("Enter the text file's path: ")
            ls = dict()
            colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']
            plot_raw(fn, ls, colors)

        else:
            folder = input("Enter the folder path to analyze: ")
            os.chdir(folder)
            ls = dict()
            colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']
            for fn in os.listdir():
                newls = plot_raw(fn, ls, colors)
                ls = newls
        plt.ylabel("current ($\mu$A)", weight='bold', fontsize=20)

    elif vgramtype == "A":
        print("all")

    elif vgramtype == "R" or vgramtype == "L" or vgramtype == "S" or vgramtype == "D":
        # raw voltammogram from dataframe
        fn = input("Enter the text file's path: ")
        datadict = makedicts(fn, vgramtype)
        plt.show()
        sys.exit()

    else:
        print("Invalid input, enter (R), (L), (S), (D), or (A)")
        sys.exit()

    plt.xlabel("potential (V)", weight='bold', fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    ax.xaxis.set_ticks(np.arange(0.5, 1.2, 0.01))
    ax.xaxis.set_major_locator(MultipleLocator(.1))
    ax.xaxis.set_minor_locator(MultipleLocator(.01))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
    plt.legend()
    plt.show()

    # elif vgramtype == "S":
    #     # smoothed
    #     print("smoothed")
    #
    # elif vgramtype == "D":
    #     # detilted
    #     print("smoothed")


