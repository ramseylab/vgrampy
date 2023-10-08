#!/usr/bin/env python3

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
import numdifftools


def get_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(description="vg2signal.py: process " +
                                         "a voltammogram into an analyte " +
                                         " peak signal value")
    arg_parser.add_argument('--log',
                            dest='log',
                            action='store_true',
                            default=False)
    arg_parser.add_argument('--bw',
                            type=float,
                            default=0.01,
                            help="kernel smoothing bandwidth (V)")
    arg_parser.add_argument('--smooth',
                            type=float,
                            default=0.00001,
                            help="smoothed spline smoothness " +
                            "parameter (bigger is smoother)")
    arg_parser.add_argument('--vcenter',
                            type=float,
                            default=1.073649114,
                            help="specify the analyte peak voltage (V)")
    arg_parser.add_argument('--vwidth',
                            type=float,
                            default=0.135,
                            help="specify the width of the analyte peak (V)")
    arg_parser.add_argument('--findCenter',
                            default=None,
                            choices=['peak', 'inf'],
                            dest='find_center',
                            help="specify a method to be used to find the"
                                 " analyte 'peak' voltage without detilting")
    arg_parser.add_argument('--recenter', action='store_true',
                            dest='recenter',
                            help="recenter the window on the empirical " +
                            "peak and then re-analyze the data with the " +
                            "new window")
    arg_parser.add_argument('--plot',
                            default=None,
                            choices=['final', 'raw', 'smoothed'],
                            dest='plot',
                            help='set to "final" to plot the detilted ' +
                            'voltammogram; set to "raw" to plot the raw data;'
                            ' set to "smoothed" to see the smoothed data')
    arg_parser.add_argument('--zoomPlot',
                            dest='zoom_plot',
                            action='store_true',
                            default=False,
                            help="plot only within the window")
    arg_parser.add_argument('filename')
    return arg_parser.parse_args()


def get_num_header_lines(file_obj: typing.TextIO) -> int:
    line_ctr = 0
    ret_ctr = None
    for line in file_obj:
        line_ctr += 1
        if line.startswith("Potential/V"):
            ret_ctr = line_ctr
    file_obj.seek(0)
    return ret_ctr


def read_raw_vg_as_df(filename: str) -> pandas.DataFrame:
    with open(filename, "r") as input_file:
        header_nlines = get_num_header_lines(input_file)
# a single chain of method calls can produce the desired
# two-column dataframe, with negative current in the "I"
# column and with the voltage in the "V" column
        return pandas.read_csv(
            input_file,
            sep=", ",
            engine="python",
            skiprows=header_nlines - 1
        ).drop(
            columns=["For(i/A)", "Rev(i/A)"]
        ).rename(
            columns={"Potential/V": "V",
                     "Diff(i/A)": "I"}
        ).apply(
            lambda r: [r[0], -1E+6 * r[1]],
            axis=1,
            raw=True)


def make_smoother(smoothing_bw: float) -> typing.Callable:
    kernel_estimator = skfda_hm.NadarayaWatsonHatMatrix(bandwidth=smoothing_bw)
    kernel_smoother = skfda_smoothing.KernelSmoother(kernel_estimator)

    def smoother_func(x: numpy.array,
                      y: numpy.array) -> numpy.array:
        fd = skfda.FDataGrid(data_matrix=y,
                             grid_points=x)
        res = kernel_smoother.fit_transform(fd).data_matrix.flatten()
        return res

    return smoother_func


def make_inf_getter(vstart: float,
                    vend: float) -> typing.Callable:
    def inf_getter_func(v: numpy.array,
                        lisd: numpy.array):
        v_in = numpy.logical_and(v >= vstart, v <= vend)
        spline_model = scipy.interpolate.UnivariateSpline(v[v_in],
                                                          lisd[v_in],
                                                          s=0,
                                                          k=3)

        v_peak = None
        # we are looking for a local minimum of the first derivative between
        # vstart and vend
        spl_mdl_dd = spline_model.derivative(n=2)
        spl_mdl_dd_pred = spl_mdl_dd(v[v_in])  # list(map(spl_mdl_dd, v[v_in]))
        spl_mdl_dd_b = scipy.interpolate.splrep(v[v_in],
                                                spl_mdl_dd_pred)
        spl_mdl_dd_ppoly = scipy.interpolate.PPoly.from_spline(spl_mdl_dd_b)
        roots_dd = spl_mdl_dd_ppoly.roots(extrapolate=False)
        if len(roots_dd) == 1:
            v_peak = float(roots_dd[0])
        elif len(roots_dd) > 1:
            print(f"NOTE: more than one inflection point found: {roots_dd} V")
            v_peak = roots_dd
        else:
            print("WARNING: no roots found")
        return (None, v_peak)
    return inf_getter_func


def make_signal_getter(vstart: float,
                       vend: float) -> typing.Callable:
    def signal_getter_func(v: numpy.array,
                           lisd: numpy.array):
        v_in = numpy.logical_and(v >= vstart, v <= vend)
        spline_model = scipy.interpolate.UnivariateSpline(v[v_in],
                                                          lisd[v_in],
                                                          s=0,
                                                          k=3)
        spl_mdl_d = spline_model.derivative(n=1)
        spl_mdl_d_pred = spl_mdl_d(v[v_in])
        spl_mdl_d_b = scipy.interpolate.splrep(v[v_in],
                                               spl_mdl_d_pred,
                                               k=3)
        spl_mdl_d_ppoly = scipy.interpolate.PPoly.from_spline(spl_mdl_d_b)
        roots_d = spl_mdl_d_ppoly.roots(extrapolate=False)
        spl_mdl_dd = numdifftools.Derivative(spline_model, n=2)
        dd_at_roots = spl_mdl_dd(roots_d)
        critical_point_v = None
        if len(dd_at_roots) > 0:
            ind_peak = numpy.argmin(dd_at_roots)
            if dd_at_roots[ind_peak] < 0:
                critical_point_v = float(roots_d[ind_peak])
        signal = None
        if critical_point_v is not None:
            signal = -dd_at_roots[ind_peak]
        return (signal, critical_point_v)
    return signal_getter_func


# smoothness: R-style smoothness parameter (non-negative)
def make_detilter(vstart: float,
                  vend: float,
                  smoothness: float) -> typing.Callable:
    assert smoothness >= 0.0, \
        "invalid smoothness parameter (should be " + \
        f"greater than zero): {smoothness}"

    def detilter_func(v: numpy.array, lis: numpy.array):
        v_out = numpy.logical_or(v < vstart, v > vend)
        lis_bg = csaps.csaps(v[v_out], lis[v_out], v,
                             smooth=(1.0 / (1.0 + smoothness)))
        return lis - lis_bg

    return detilter_func


def v2signal(vg_filename: str,
             do_log: bool,
             smoothing_bw: float,
             vcenter: float,
             vwidth: float,
             smoothness_param: float,
             find_center: str):

    vg_df = read_raw_vg_as_df(vg_filename)

    vstart = vcenter - 0.5*vwidth
    vend = vcenter + 0.5*vwidth

    if do_log:
        cur_var_name = "logI"
        vg_df[cur_var_name] = numpy.log2(vg_df["I"])
    else:
        cur_var_name = "I"

    smoother = make_smoother(smoothing_bw)

    vg_df["smoothed"] = smoother(vg_df["V"], vg_df[cur_var_name].to_numpy())

    signal_getter = make_signal_getter(vstart, vend)

    if find_center is not None:
        if find_center == 'peak':
            (peak_signal, peak_v) = signal_getter(vg_df["V"],
                                                  vg_df["smoothed"])
        elif find_center == 'inf':
            inf_getter = make_inf_getter(vstart, vend)
            (peak_signal, peak_v) = inf_getter(vg_df["V"],
                                               vg_df["smoothed"])
            # handle inflection here
        else:
            assert False, f"Invalid find_center value: {find_center}"
    else:
        detilter = make_detilter(vstart, vend, smoothness_param)
        vg_df["detilted"] = detilter(vg_df["V"].to_numpy(),
                                     vg_df["smoothed"].to_numpy())
        (peak_signal, peak_v) = signal_getter(vg_df["V"], vg_df["detilted"])

    return (peak_signal, peak_v, vg_df)


if __name__ == '__main__':
    args = get_args()
    assert not (args.recenter and args.plot), \
        "Cannot specify both recenter and plot at the same time"

    assert not (args.recenter and args.find_center), \
        "Cannot specify both recenter and findCenter at" + \
        " the same time"

    assert not (args.find_center is not None and args.plot == 'final'), \
        "Cannot specify both findCenter and plot=final at same time"

    vg_filename = args.filename
    vcenter = args.vcenter
    vwidth = args.vwidth
    assert vwidth > 0.0, f"vwidth must be nonnegative: {vwidth}"

    do_log = args.log

    smoothing_bw = args.bw
    assert smoothing_bw >= 0.0, "smoothing bandwidth must be " + \
        f"nonnegative: {smoothing_bw}"

    smoothness_param = args.smooth
    assert smoothness_param >= 0.0, "smoothness param must be " + \
        f"nonnegative: {smoothness_param}"

    (peak_signal, peak_v, vg_df) = v2signal(vg_filename,
                                            do_log,
                                            smoothing_bw,
                                            vcenter,
                                            vwidth,
                                            smoothness_param,
                                            args.find_center)

    vstart = vcenter - 0.5*vwidth
    vend = vcenter + 0.5*vwidth

    if peak_v is not None:
        if type(peak_v) == float:
            print(f"Analyte at: {peak_v:0.3f} V")
        elif peak_v.size > 1:
            i = 0
            for peak_v_i in peak_v:
                i += 1
                print(f"Peak number {i}: ")
                print(f"  Analyte at: {peak_v_i:0.3f} V")
        if peak_signal is not None:
            print(f"Signal: {peak_signal:0.3f} 1/V^2")
        if args.recenter:
            assert type(peak_v) != list
            (peak_signal, peak_v, vg_df) = v2signal(vg_filename,
                                                    do_log,
                                                    smoothing_bw,
                                                    peak_v,
                                                    vwidth,
                                                    smoothness_param,
                                                    None)
            if peak_signal is not None:
                print(f"Recentered peak voltage: {peak_v:0.3f} V")
                print(f"Recentered peak Signal: {peak_signal:0.3f} 1/V^2")
            else:
                print("no peak detected with recentered window; try --plot")
    else:
        print("no peak detected in original window; try running with --plot")

    if args.plot is not None:
        y_axis_label = "peak current"
        if args.plot == 'final':
            y_vals_to_plot = vg_df["detilted"]
            y_axis_label = y_axis_label + ', normalized'
        elif args.plot == 'raw':
            if args.log:
                y_vals_to_plot = vg_df['logI']
            else:
                y_vals_to_plot = vg_df['I']
            y_axis_label = y_axis_label + ', un-normalized'
        elif args.plot == 'smoothed':
            y_vals_to_plot = vg_df['smoothed']
        if args.log:
            y_axis_label = 'log ' + y_axis_label
        if not args.zoom_plot:
            x = vg_df["V"]
            y = y_vals_to_plot
            plt.plot(x, y, "b-")
        else:
            vr = numpy.logical_and(vg_df["V"] > vstart,
                                   vg_df["V"] < vend)
            x = vg_df["V"][vr]
            y = y_vals_to_plot[vr]
            plt.plot(x, y, "b.")
        plt.xlabel('baseline potential (V)')
        plt.ylabel(y_axis_label)
        plt.show()
