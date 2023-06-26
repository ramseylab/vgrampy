# vgrampy

### Author: Stephen Ramsey
### Date: June 26, 2023

Python tools for analyzing electrochemistry voltammograms. The script
`vg2signal.py` processes a potentiostat voltammogram data file using a method
analogous to LDNH, into a signal value and optionally plots the "detilted"
voltammogram. It can also optionally re-center the analysis window on the
empirical peak voltage from the first phase of analysis of the data (which is
_only_ a good idea to run on a voltammogram that has a clear and unambiguous
analyte peak).

# Prerequisites for using this software

- Python 3.9 (on Apple Silicon, it doesn't yet work on Python 3.11)
- `git`
- `bash` shell

So far, this software has only been tested on MacOS 12.6.5 on Apple M1. It has 
not been tested on Windows/x86_64, Linux/x86_64, etc.

# How to install and run `vg2signal.py`:

These instructions assume that you know how to use the bash shell (and modify
your PATH if necessary), and that you are in an interactive bash session

1. Clone the software repo

```
git clone git@github.com:ramseylab/vgrampy.git
```

2. Change directory into the software repo

```
cd vgrampy
```

3. Install a Python virtualenv, assuming `PYTHON` is a placeholder for a command
that runs a "vgrampy"-compatible python (for example, `/usr/bin/python3` on MacOS
12.6.5):

```
PYTHON -m venv venv
```

so on MacOS 12.6.5, the above would be:

```
/usr/bin/python3 -m venv venv
```

4. Install the required packages

```
venv/bin/pip3 install -r requirements.txt
```

5. Run `vg2signal.py` on your voltammogram `VGRAM.txt`


```
venv/bin/python3 vg2signal.py VGRAM.txt
```

where, of course, `VGRAM.txt` needs to be in the local
working directory or you need to specify the path to it, like

```
venv/bin/python3 vg2signal.py /path/to/VGRAM.txt
```

# Options for `vg2signal.py`:

- `--plot`: a present/absent optional argument that displays a plot of the
  detilted voltammogram
- `--bw`: a floating point argument that specifies the bandwidth for kernel
  density smoothing of the log-transformed voltammogram; default value is 0.02
  (determined empirically on limited data using inspection; may not be optimal)
- `--smooth`: a floating point argument that specifies the smoothing parameter
for the smooth cubic spline fit for detilting; default value is 0.0000001
(determined empirically on limited data using inspection; may not be optimal)
- `--help`: display concise help text for the command-line options for `vg2signalpy`
- `--recenter`: analyze the voltammogram twice; the second time, use a window
that is centered on the empirically determined peak voltage from the first run
(so-called "double-detilting")
- `--vcenter`: specify the voltage where the analyte peak is expected (default
value is `1.073649114`; this will likely need tuning depending on your specific
experimental conditions, electrode treatment, saliva background, etc.)
- `--vwidth`: specify the width of the window for data censoring for fitting the
background voltammogram for detilting; defaults to `0.135`; this will likely
need tuning depending on your specific experimental conditions, electrode
treatment, saliva background, etc.)

