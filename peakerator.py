import pandas
import scipy.interpolate
import typing
import matplotlib.pyplot as plt
import argparse
import numpy


def get_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(description="peakerator.py: find " +
                                         "the peak or inflection point in a " +
                                         "voltammogram")
    gpi = arg_parser.add_mutually_exclusive_group(required=True)
    gpi.add_argument('--peak', action="store_true", default=False)
    gpi.add_argument('--inf', action='store_true', default=False)
    arg_parser.add_argument('--smooth', type=float, default=0.01)
    arg_parser.add_argument('--plot', action='store_true', default=False)
    arg_parser.add_argument('--log', dest='log', action='store_true',
                            default=False)
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
    with open(vg_filename, "r") as input_file:
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


if __name__ == '__main__':
    args = get_args()

    vg_filename = args.filename
    vg_df = read_raw_vg_as_df(vg_filename)

    if args.log:
        vg_df["I"] = numpy.log10(vg_df["I"])

    smooth = args.smooth

    spline_model = scipy.interpolate.UnivariateSpline(vg_df["V"],
                                                      vg_df["I"],
                                                      k=4,
                                                      s=smooth)
    spline_model_d = spline_model.derivative(n=1)
    roots_d = spline_model_d.roots()
    spline_model_dd = spline_model.derivative(n=2)

    if args.peak:
        critical_point_v = None
        dd_at_roots = numpy.array(list(map(spline_model_dd, roots_d)))
        if len(dd_at_roots) > 0:
            ind_peak = numpy.argmin(dd_at_roots)
            if dd_at_roots[ind_peak] < 0:
                critical_point_v = roots_d[ind_peak]

        if critical_point_v is not None:
            print(f"Voltage for peak: {critical_point_v:0.3f} V")
        else:
            print("Failed to find peak")
    elif args.inf:
        inflection_point_v = None
        spline_model = scipy.interpolate.UnivariateSpline(vg_df["V"],
                                                          vg_df["I"],
                                                          k=5,
                                                          s=smooth)
        spline_model_dd = spline_model.derivative(n=2)
        spline_model_ddd = spline_model.derivative(n=3)

        roots_dd = spline_model_dd.roots().tolist()

        ddd_at_roots = numpy.array(list(map(spline_model_ddd, roots_dd)))
        if len(ddd_at_roots) > 0:
            ind_inf = numpy.argmax(ddd_at_roots)
            if ddd_at_roots[ind_inf] > 0:
                inflection_point_v = roots_dd[ind_inf]

        if inflection_point_v is not None:
            print(f"Voltage for inflection point: {inflection_point_v:0.3f} V")
        else:
            print("Failed to find inflec. point")
    else:
        assert False, "should not get here"

    if args.plot:
        plt.plot(vg_df["V"], vg_df["I"], "b-")
        plt.plot(vg_df["V"], spline_model(vg_df["V"]), "g-")
        if args.peak:
            x_mark_v = critical_point_v
        elif args.inf:
            x_mark_v = inflection_point_v
        else:
            assert False, "should not get here"
        if x_mark_v is not None:
            plt.plot(x_mark_v, spline_model(x_mark_v), "rx")
        plt.show()
