import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import sys
import pandas as pd
from operator import itemgetter

"""
plotraw(filename, labels)
- plots raw voltammogram from text files
- return: labels of concentrations & colors for legend
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
        conc_str = str(float(conc)) + " \u03BCM"
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


"""
def makedicts
- gathers potential, current of choice (raw, log, smoothed, detilted)
- return: dictionary of ([concentration]: (potential, current)
"""


def figformat():
    plt.xlabel("potential (V)", weight='bold', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    ax.xaxis.set_ticks(np.arange(0.5, 1.2, 0.01))
    ax.xaxis.set_major_locator(MultipleLocator(.1))
    ax.xaxis.set_minor_locator(MultipleLocator(.01))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
    plt.show()


"""
def makedicts
- gathers potential, current of choice (raw, log, smoothed, detilted)
- return: dictionary of ([concentration]: (potential, current)
"""


def makedicts(file, ytype, multiple):
    df = pd.read_excel(file)
    dicttype = dict()
    concs = set((l[0], l[1]) for l in df.values)
    ylabelreturn = ""
    ytitlereturn = ""
    for c, d in concs:
        if (d == multiple[0] and c == multiple[1]) or multiple == "M":
            x = [l[2] for l in df.values if l[0] == c and l[1] == d]
            if ytype == "R":
                y = [l[3] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'current ($\mu$A)'
                ytitlereturn = "raw voltammogram"
            elif ytype == "L":
                y = [l[4] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'log-transform current'
                ytitlereturn = "log voltammogram"
            elif ytype == "S":
                y = [l[-2] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'log-transform current'
                ytitlereturn = "smoothed voltammogram"
            else:
                y = [l[-1] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'normalized current'
                ytitlereturn = "detilted voltammogram"
            dicttype[(c, d)] = (x, y)

    return dicttype, ylabelreturn, ytitlereturn


"""
def plotdataframe
- plots the potential, chosen current (raw, log, smoothed, detilted)
"""


def plotdataframe(datadf, sep):
    colors = ['tab:orange', 'tab:blue', 'tab:orange', 'tab:red', 'tab:green', 'black']  # colors to plot different concs
    colorconc = dict()
    keys = sorted(datadf.keys(), key=itemgetter(0))
    for key in keys:
        val = datadf[key]
        print(key)
        labelname = str(key[0]) + ' \u03BCM'

        if key[0] not in colorconc.keys():
            color = colors.pop()
            colorconc[key[0]] = color
        else:
            color = colorconc[key[0]]
        plt.plot(val[0], val[1], label=labelname, color=color)  # colors based on concentration
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())


"""
main
- prompts user to choose plot type
"""

if __name__ == '__main__':
    filetype = input("Do you have a Dataframe file (D) or text (T)?: ")
    multiple = input("Would you like to plot one (O) or multiple (M) voltammograms?: ")

    if multiple != "O" and multiple != "M":
        print("Invalid input, enter (O) or (M)")
        sys.exit()

    if filetype == "D":
        vgramtype = input(
            "Would you like to plot raw (R), log (L), smoothed (S), detilted (D), or all (A) voltammograms?: ")
    else:
        vgramtype = "raw"
    fig, ax = plt.subplots()
    if vgramtype == "raw":
        print("raw")
        if multiple == "M":
            folder = input("Enter the folder path to analyze: ")
            os.chdir(folder)
            ls = dict()
            colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']
            for fn in os.listdir():
                newls = plot_raw(fn, ls, colors)
                ls = newls
        else:
            print("one")
            fn = input("Enter the text file's path: ")
            ls = dict()
            colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']
            plot_raw(fn, ls, colors)
        plt.ylabel("current ($\mu$A)", weight='bold', fontsize=12)
        plt.title("raw voltammogram", weight='bold', fontsize=15)

    elif filetype == "D":
        fn = input("Enter the dataframes's path: ")
        if multiple == "O":
            dev = int(input("Enter the device to plot: "))
            conc = float(input("Enter the concentration to plot: "))
            multiple = [dev, conc]
        else:
            sep = input("Would you like to separate by concentration (Y/N)? ")
            if sep == "Y":
                sep == True
            else:
                sep == False

        if vgramtype == "A":
            vgrams = ["R", "L", "S", "D"]

            for vgram in vgrams:
                datadict, ylabel, ytitle = makedicts(fn, vgram, multiple)
                plotdataframe(datadict, sep)
                plt.ylabel(ylabel, weight='bold', fontsize=12)
                plt.title(ytitle, weight='bold', fontsize=15)
                figformat()
        else:
            # voltammogram from dataframe
            datadict, ylabel, ytitle = makedicts(fn, vgramtype, multiple)
            plotdataframe(datadict, sep)
            plt.ylabel(ylabel, weight='bold', fontsize=12)
            plt.title(ytitle, weight='bold', fontsize=15)
            figformat()

    else:
        print("Invalid input, enter (R), (L), (S), (D), or (A)")
        sys.exit()

    # format figures:
    if vgramtype != "A":
        figformat()
