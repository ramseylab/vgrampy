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


def get_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(description="vg2signal.py: process " +
                                         "a voltammogram into an analyte " +
                                         " peak signal value")
    arg_parser.add_argument('--log', dest='log', action='store_true',
                            default=False)
    arg_parser.add_argument('--bw', type=float, default=0.02,
                            help="kernel smoothing bandwidth (V)")
    arg_parser.add_argument('--smooth', type=float, default=0.0000001,
                            help="smoothed spline smoothness " +
                            "parameter (bigger is smoother)")
    arg_parser.add_argument('--vcenter', type=float, default=1.073649114,
                            help="specify the analyte peak voltage (V)")
    arg_parser.add_argument('--vwidth', type=float, default=0.135,
                            help="specify the width of the analyte peak (V)")
    gpi = arg_parser.add_mutually_exclusive_group()
    gpi.add_argument('-p', '--plot', action='store_true', dest='plot',
                     help='set to true in order to plot the detilted ' +
                     'voltammogram')
    gpi.add_argument('-s', '--signal', action='store_true', dest='signal',
                     help='set to true in order to compute a "signal" value')
    arg_parser.set_defaults(signal=True)
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


def make_signal_getter(vstart: float,
                       vend: float) -> typing.Callable:
    def signal_getter_func(v: numpy.array,
                           lisd: numpy.array):
        v_in = numpy.logical_and(v >= vstart, v <= vend)
        spline_model = scipy.interpolate.UnivariateSpline(v[v_in],
                                                          lisd[v_in],
                                                          k=4)
        spline_model_d = spline_model.derivative(n=1)
        roots_d = spline_model_d.roots()
        spline_model_dd = spline_model.derivative(n=2)
        dd_at_roots = numpy.array(list(map(spline_model_dd, roots_d)))
        critical_point_v = None
        if len(dd_at_roots) > 0:
            ind_peak = numpy.argmin(dd_at_roots)
            if dd_at_roots[ind_peak] < 0:
                critical_point_v = roots_d[ind_peak]
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
             smoothness_param: float):

    vg_df = read_raw_vg_as_df(vg_filename)

    vstart = vcenter - 0.5*vwidth
    vend = vcenter + 0.5*vwidth

    if do_log:
        cur_var_name = "logI"
        vg_df[cur_var_name] = numpy.log10(vg_df["I"])
    else:
        cur_var_name = "I"

    smoother = make_smoother(smoothing_bw)

    vg_df["smoothed"] = smoother(vg_df["V"], vg_df[cur_var_name].to_numpy())

    detilter = make_detilter(vstart, vend, smoothness_param)
    vg_df["detilted"] = detilter(vg_df["V"].to_numpy(),
                                 vg_df["smoothed"].to_numpy())

    if args.plot:
        plt.plot(vg_df["V"], vg_df["detilted"], "b-")
        plt.show()
    else:
        signal_getter = make_signal_getter(vstart, vend)
        (peak_signal, peak_v) = signal_getter(vg_df["V"], vg_df["detilted"])

        if peak_signal is not None:
            print(f"Peak voltage: {peak_v:0.3f} V")
            print(f"Signal: {peak_signal:0.3f} 1/V^2")
        else:
            print("no peak detected")


if __name__ == '__main__':
    args = get_args()

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

    v2signal(vg_filename,
             do_log,
             smoothing_bw,
             vcenter,
             vwidth,
             smoothness_param)
