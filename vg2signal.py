import pandas
import scipy
import typing
import numpy
import skfda.misc.hat_matrix as skfda_hm
import skfda.preprocessing.smoothing as skfda_smoothing
import skfda
import csaps
import numdifftools
from sklearn import metrics

"""
get_num_header_lines
- used by read_raw_vg_as_df to get number of rows to skip
"""


def get_num_header_lines(file_obj: typing.TextIO, start_voltage:str) -> int:
    line_ctr = 0
    ret_ctr = None
    omit_start = None
    omit_end = None
    for line in file_obj:
        line_ctr += 1
        if line.startswith(start_voltage):
            omit_end = line_ctr
    file_obj.seek(0)
    return omit_end


"""
read_raw_vg_as_df
- take the text file and gets the current & potential
- return: dataframe of current & potential
"""


def read_raw_vg_as_df(filename: str, start_voltage:str) -> pandas.DataFrame:
    with open(filename, "r") as input_file:
        omit_e = get_num_header_lines(input_file, start_voltage)
        # a single chain of method calls can produce the desired
        # two-column dataframe, with negative current in the "I"
        # column and with the voltage in the "V" column
        return pandas.read_csv(
            input_file,
            sep=", ",
            engine="python",
            skiprows=omit_e-1,
            usecols=[0, 1],
            names=["V", "I"]
        ).apply(
            lambda r: [r[0], -1E+6 * r[1]],
            axis=1,
            raw=True)

"""
make_shoulder_getter
- takes a rough voltage location of peak shoulder
- retrun: voltage location of peak shoulder used as "vcenter"
"""


def make_shoulder_getter(vstart: float,
                         vend: float) -> typing.Callable:
    def shoulder_getter_func(v: numpy.array,
                             lisd: numpy.array):
        v_in = numpy.logical_and(v >= vstart, v <= vend)
        spline_model = scipy.interpolate.UnivariateSpline(v[v_in],
                                                          lisd[v_in],
                                                          s=0,
                                                          k=4)

        # we are looking for a local minimum of the third derivative between
        # vstart and vend
        spl_mdl_dd = spline_model.derivative(n=2)
        spl_mdl_dd_pred = spl_mdl_dd(v[v_in])

        spl_mdl_ddd = spline_model.derivative(n=3)
        spl_mdl_ddd_pred = spl_mdl_ddd(v[v_in])
        spl_mdl_ddd_b = scipy.interpolate.splrep(v[v_in],
                                                 spl_mdl_ddd_pred)
        spl_mdl_ddd_ppoly = scipy.interpolate.PPoly.from_spline(spl_mdl_ddd_b)
        roots_ddd = spl_mdl_ddd_ppoly.roots(extrapolate=False)
        if len(roots_ddd) == 1:
            v_peak = float(roots_ddd[0])
        elif len(roots_ddd) > 1:  # if multiple third derivatives
            minsecond = min(spl_mdl_dd_pred)
            idx = (numpy.abs(spl_mdl_dd_pred - minsecond)).argmin()
            vin = list(v[v_in])
            v_peak = vin[idx]
        else:  # if no third derivative, get minimum of second derivative
            minsecond = min(spl_mdl_dd_pred)
            idx = (numpy.abs(spl_mdl_dd_pred - minsecond)).argmin()
            vin = list(v[v_in])
            v_peak = vin[idx]
            print("WARNING: no roots found")
        return None, v_peak
    return shoulder_getter_func


"""
make_smoother
- uses kernel smoother to smooth the data
- return: the smoothed current
"""


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


"""
make_signal_getter
- gets signal metric (curvature, area, height) around peak
- return: the signal metric
"""


def make_signal_getter(vstart: float,
                       vend: float) -> typing.Callable:
    def signal_getter_func(v: numpy.array,
                           lisd: numpy.array):
        v_in = numpy.logical_and(v >= vstart, v <= vend)
        spline_model = scipy.interpolate.UnivariateSpline(v[v_in],
                                                          lisd[v_in],
                                                          s=0,
                                                          k=4)
        spline_model_d = spline_model.derivative(n=1)
        spline_model_d_ppoly = scipy.interpolate.splrep(v[v_in],
                                                        list(map(spline_model_d,
                                                                 v[v_in])), k=4)
        roots_d = scipy.interpolate.PPoly.from_spline(spline_model_d_ppoly).roots(extrapolate=False)
        spline_model_dd = numdifftools.Derivative(spline_model, n=2)
        dd_at_roots = numpy.array(list(map(spline_model_dd, roots_d)))
        critical_point_v = None
        ind_peak = None
        if len(dd_at_roots) > 0:
            ind_peak = numpy.argmin(dd_at_roots)
            if dd_at_roots[ind_peak] < 0:
                critical_point_v = roots_d[ind_peak]
        signal = None
        if critical_point_v is not None:
            signal = -dd_at_roots[ind_peak]
        return signal, critical_point_v
    return signal_getter_func


"""
make_detilter
- subtracts smoothed data from function interpolated without drug peak
- return: detilted (normalized) current
"""


def make_detilter(vstart: float,
                  vend: float,
                  stiffness: float) -> typing.Callable:
    assert stiffness >= 0.0, \
        "invalid stiffness parameter (should be " + \
        f"greater than or equal to zero): {stiffness}"

    def detilter_func(v: numpy.array, lis: numpy.array):
        v_out = numpy.logical_or(v < vstart, v > vend)
        # stiffness: R-style stiffness parameter (non-negative)
        lis_bg = csaps.csaps(v[v_out], lis[v_out], v,
                             smooth=(1.0 / (1.0 + stiffness)))
        return lis - lis_bg
    return detilter_func


"""
vg2signal
- main function for vg2signal.py
- log transform (if indicated), smooth, detilt, and get signal metric for a voltammogram
- return: signal metric, voltage of peak, dataframe of transformed data at each V, calculated peak center
"""


def v2signal(vg_filename: str,
             do_log: bool,
             peak_feat: int,
             smoothing_bw: float,
             vwidth: float,
             stiffness: float,
             v_start: str,
             pv_min: float,
             pv_max: float):

    vg_df = read_raw_vg_as_df(vg_filename, v_start)

    if do_log:
        cur_var_name = "logI"
        vg_df[cur_var_name] = numpy.log2(vg_df["I"])
    else:
        cur_var_name = "I"

    smoother = make_smoother(smoothing_bw)

    vg_df["smoothed"] = smoother(vg_df["V"], vg_df[cur_var_name].to_numpy())

    shoulder_getter = make_shoulder_getter(pv_min, pv_max)  # 1-1.1V is approx peak location
    (peak_signal, peak_v_shoulder) = shoulder_getter(vg_df["V"],
                                                     vg_df["smoothed"])

    vcenter = peak_v_shoulder
    vstart = vcenter - 0.5*vwidth
    vend = vcenter + 0.5*vwidth

    detilter = make_detilter(vstart, vend, stiffness)
    vg_df["detilted"] = detilter(vg_df["V"].to_numpy(),
                                 vg_df["smoothed"].to_numpy())

    signal_getter = make_signal_getter(vstart, vend)
    (peak_curve_return, peak_v_return) = signal_getter(vg_df["V"], vg_df["detilted"])
    ymaxidx = numpy.argmax(vg_df["detilted"])

    peakarea = metrics.auc(vg_df["V"], vg_df["detilted"])*1000
    peakheight = vg_df["detilted"][ymaxidx]

    if peak_feat == 1:  # if signal metric is peak curvature
        peak_signal_return = peak_curve_return
    elif peak_feat == 2:  # if signal metric is peak height
        peak_signal_return = peakheight
    else:
        peak_signal_return = peakarea  # if signal metric is peak area

    return peak_signal_return, peak_v_return, vg_df, vcenter
