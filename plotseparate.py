import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import sys

"""
plotraw(filename, labels)
"""


def plot_raw(filename, labels):
    if filename[-3:] == 'txt':
        print("plotting file:", filename)
        fp = open(filename, 'r')
        xs = []
        ys = []
        idx1 = filename.rfind("cbz")
        idx2 = filename[idx1:].find("_")
        conc = filename[idx1 + 3:idx1 + idx2]
        # add concentration better
        if conc == "00":
            c = 'black'
            conc_str = '0 \u03BCM'
        elif conc == "7p5":
            c = 'red'
            conc_str = '7.5 \u03BCM'
        else:
            c = 'blue'
            conc_str = '15 \u03BCM'

        for line in fp:
            if line[0].isnumeric():
                potential, diff, f, rev = line.split(',')
                potential = float(potential)
                current = -float(diff) * 1000000
                xs.append(potential)
                ys.append(current)
        if labels is None:
            plt.plot(xs, ys, color=c, label=conc_str)
            labels.append(conc_str)
        elif conc_str in labels:
            plt.plot(xs, ys, color=c)
        else:
            plt.plot(xs, ys, color=c, label=conc_str)
            labels.append(conc_str)
    return labels


if __name__ == '__main__':
    multiple = input("Would you like to plot one (O) or multiple (M) voltammograms?: ")
    if multiple != "O" and multiple != "M":
        print("Invalid input, enter (O) or (M)")
        sys.exit()

    vgramtype = input("Would you like to plot raw (R), smoothed (S), detilted (D), or all (A) voltammograms?: ")
    fig, ax = plt.subplots()

    if vgramtype == "R":
        if multiple == "O":
            fn = input("Enter the text file's path: ")
            ls = []
            plot_raw(fn, ls)

        else:
            folder = input("Enter the folder path to analyze: ")
            os.chdir(folder)
            ls = []
            for fn in os.listdir():
                newls = plot_raw(fn, ls)
                ls = newls
        plt.ylabel("Current ($\mu$A)", weight='bold', fontsize=20)

    elif vgramtype == "S":
        # smoothed
        print("smoothed")

    elif vgramtype == "D":
        # detilted
        print("smoothed")

    elif vgramtype == "A":
        print("all")

    else:
        print("Invalid input, enter (R), (S), (D), or (A)")
        sys.exit()

    plt.xlabel("Potential (V)", weight='bold', fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    ax.xaxis.set_ticks(np.arange(0.5, 1.2, 0.01))
    ax.xaxis.set_major_locator(MultipleLocator(.1))
    ax.xaxis.set_minor_locator(MultipleLocator(.01))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
    plt.legend()
    plt.show()
