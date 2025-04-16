import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for saving plots
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd
from operator import itemgetter

"""
plotraw(filename, labels)
- plots raw voltammogram from text files
- return: labels of concentrations & colors for legend
"""


def plot_raw(filename, labels, colorslst):
    if filename[-3:] == 'txt':  # if text file
        print("plotting file:", filename)
        fp = open(filename, 'r')  # open file
        xs = []
        ys = []
        idx1 = filename.rfind("cbz")
        idx2 = filename[idx1:].find("_")
        conc = filename[idx1 + 3:idx1 + idx2]  # get concentration

        if 'p' in conc:  # for '7p5' concentration
            pi = conc.find('p')
            conctemp = conc[:pi] + '.' + conc[pi + 1:]
            conc = conctemp
        conc_str = str(float(conc)) + " \u03BCM"
        for line in fp:  # for each current, voltage line
            if line[0].isnumeric():
                potential, diff, f, rev = line.split(',')
                potential = float(potential)
                current = -float(diff) * 1000000
                xs.append(potential)  # add potential
                ys.append(current)  # add current
        labelkeys = list(labels.keys())
        if conc_str in labelkeys:
            plt.plot(xs, ys, color=labels[conc_str])
        else:
            if len(labelkeys) > 0:
                plt.legend()
                plt.ylabel("current ($\mu$A)", weight='bold', fontsize=12)
                plt.title("raw voltammogram", weight='bold', fontsize=15)
                plt.xlabel("potential (V)", weight='bold', fontsize=12)
            newcolor = colorslst.pop()
            plt.plot(xs, ys, color=newcolor, label=conc_str)
            labels[conc_str] = newcolor
    return labels


"""
def makedicts
- gathers potential, current of choice (raw, log, smoothed, detilted)
- return: dictionary of ([concentration]: (potential, current)
"""


def makedicts(file, ytype, multiple):
    df = pd.read_excel(file)  # read dataframe.xlsx
    dicttype = dict()
    concs = set((l[0], l[1]) for l in df.values)  # conc, device set
    ylabelreturn = ""
    ytitlereturn = ""
    for c, d in concs:  # for conc, device
        if (d == multiple[0] and c == multiple[1]) or multiple == "M":  # if plotting multiple or if selected device
            x = [l[2] for l in df.values if l[0] == c and l[1] == d]  # potential
            if ytype == "R":  # if raw voltammogram
                y = [l[3] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'current ($\mu$A)'
                ytitlereturn = "raw voltammogram"
            elif ytype == "L":  # if log-transform voltammogram
                y = [l[4] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'log-transform current'
                ytitlereturn = "log voltammogram"
            elif ytype == "S":  # if smoothed voltammogram
                y = [l[-2] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'log-transform current'
                ytitlereturn = "smoothed voltammogram"
            else:  # if detilted voltammogram
                y = [l[-1] for l in df.values if l[0] == c and l[1] == d]
                ylabelreturn = 'normalized current'
                ytitlereturn = "detilted voltammogram"
            dicttype[(c, d)] = (x, y)  # add device, conc's current and potential

    return dicttype, ylabelreturn, ytitlereturn


"""
def plotdataframe
- plots the potential, chosen current (raw, log, smoothed, detilted)
"""


def plotdataframe(datadf, sepbyconc):
    colors = ['tab:orange', 'tab:blue', 'tab:orange', 'tab:red', 'tab:green', 'black']  # colors to plot different concs
    colorconc = dict()
    keys = sorted(datadf.keys(), key=itemgetter(0))
    for key in keys:  # for concentration, device in dataframe
        val = datadf[key]
        labelname = str(key[0]) + ' \u03BCM'
        # if new concentration to plot
        if key[0] not in colorconc.keys():
            color = colors.pop()
            if sepbyconc and colorconc.keys():  # if separating plots by concentration
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                plt.legend(by_label.values(), by_label.keys())
                plt.ylabel(ylabel, weight='bold', fontsize=12)
                plt.title(ytitle, weight='bold', fontsize=15)
                plt.xlabel("potential (V)", weight='bold', fontsize=12)
                plt.show()
            colorconc[key[0]] = color
        else:
            color = colorconc[key[0]]
        plt.plot(val[0], val[1], label=labelname, color=color)  # colors based on concentration
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())  # plot only one legend per conc


"""
main
- prompts user to choose plot type
"""

if __name__ == '__main__':
    filetype = input("Do you have a Dataframe file (D) or text (T)?: ")
    multiple = input("Would you like to plot one (O) or multiple (M) voltammograms?: ")

    if multiple != "O" and multiple != "M":  # if invalid entry
        print("Invalid input, enter (O) or (M)")
        sys.exit()

    if filetype == "D":  # if plotting from dataframe
        vgramtype = input(
            "Would you like to plot raw (R), log (L), smoothed (S), detilted (D), or all (A) voltammograms?: ")
    else:  # if plotting from text file
        vgramtype = "raw"
    fig, ax = plt.subplots()

    if vgramtype == "raw":  # if plotting from text file
        if multiple == "M":  # multiple voltammograms
            folder = input("Enter the folder path to analyze: ")
            os.chdir(folder)  # change directory to folder
            ls = dict()
            colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']
            for fn in os.listdir():
                newls = plot_raw(fn, ls, colors)
                ls = newls  # labels for legend
        else:  # one voltammogram
            fn = input("Enter the text file's path: ")
            ls = dict()
            colors = ['tab:green', 'tab:blue', 'tab:red', 'tab:purple', 'tab:orange']
            plot_raw(fn, ls, colors)
        plt.ylabel("current ($\mu$A)", weight='bold', fontsize=12)
        plt.title("raw voltammogram", weight='bold', fontsize=15)
        plt.show()

    elif filetype == "D":  # if plotting from a dataframe
        fn = input("Enter the dataframes's path: ")
        sepplot = False  # do not separate by concentration
        if multiple == "O":  # if plotting one voltammogram
            dev = int(input("Enter the device to plot: "))
            conc = float(input("Enter the concentration to plot: "))
            multiple = [dev, conc]
        else:  # if plotting multiple voltammograms
            sep = input("Would you like to separate by concentration (Y/N)? ")
            if sep == "Y":  # separate by concentration
                sepplot = True

        if vgramtype == "A":  # if plotting all types of voltammogram
            vgrams = ["R", "L", "S", "D"]  # Raw, Log, Smooth, Detilted
        else:
            vgrams = [vgramtype]

        for vgram in vgrams:  # for each type of voltammogram
            datadict, ylabel, ytitle = makedicts(fn, vgram, multiple)
            plotdataframe(datadict, sepplot)
            plt.ylabel(ylabel, weight='bold', fontsize=12)
            plt.title(ytitle, weight='bold', fontsize=15)
            plt.xlabel("potential (V)", weight='bold', fontsize=12)
            plt.show()
    else:
        print("Invalid input, enter (R), (L), (S), (D), or (A)")
        sys.exit()
