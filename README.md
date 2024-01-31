# vgrampy

### Author: Noel Lefevre (Adapted from Steven Ramsey's LDNH README.md)
### Date: January 29, 2024

Python tools for analyzing electrochemistry voltammograms. The script
`vg2signal.py` processes a potentiostat voltammogram data file using a method
analogous to LDNH, into a signal value and optionally plots the "detilted"
voltammogram. It can also optionally re-center the analysis window on the
empirical peak voltage from the first phase of analysis of the data (which is
_only_ a good idea to run on a voltammogram that has a clear and unambiguous
analyte peak).

# Prerequisites for using this software

- Python 3.9 (`scikit-learn` package does not work on any later version)
- `git`
- Coding Application/IDE
- A github account

So far, this software has only been tested on Windows11/x86_64. It has 
not been tested on MacOS 12.6.5 on Apple M1, Linux/x86_64, etc.

# How to install and run `groupvg2.py` for `user-friendly` branch:

1. Download Python 3.9 (can be 3.9.0-3.9.12)
   1. make sure to select `Add Python 3.9 to PATH` when you install it


2. Download a coding application/IDE (i.e. VisualStudio, VSCode, PyCharm)


3. Clone the software repo (2 ways)
   1. sign into your github through the IDE
   2. paste the repo address: `https://github.com/ramseylab/vgrampy.git`


4. Change to the correct branch- for running for one experiment use `user-friendly`
   1. for VisualStudio- on the right side click `Git Changes` and change the drop-down menu


5. Open the command prompt and change your directory to the software repo `cd grampy`
   1. if you open the command prompt within your IDE, it should already be in the right directory


6. Install all of the required packages:
```dockerignore
pip install numpy
```
- depending on your computer, it may be `pip` or `pip3`
- most packages will be installed when creating the virtual environment

7. Run the program by typing in 
```
python groupvg2.py
```
- depending on your computer, it may be `python` or `python3` or `py`

# Options for `groupvg2.py`:

### There are default parameters applied to the code, but you can change them if needed

- **Log-Transformation**: log-transform or not (default = log)
- **Peak Feature**: peak curvature, height or area (default = peak curvature)
- **Smoothing Parameter**: amount of smoothing the voltammogram (default = 0.006)
- **Stiffness Parameter**: how strictly the spline passes through the data points (default = 0)
- **Window Width**: voltage width to window out when making the spline (default = 0.15)

# Plotting In `groupvg2.py`:

#### You can choose whether or not to plot, and whether to separate those plots by concentration
#### The plots saved will be the smoothed and detilted voltammograms, more options are in `plotseparate.py`

# Output Files

## There are 3 files created by running `groupvg2.py`

The naming convention for each file is: `[filename]_[log or no log]_[smoothing parameter]_[stiffness parameter]_[window width]`

For example `dataframe_log_curvature_0.006_0_0.15.xlsx`

### 1. A dataframe excel file that has each replicates' data:

| conc | replicate | V     | I       | logI     | smoothed | detilted |
|------|-----------|-------|---------|----------|:---------|----------|
| 0    | 1         | 0.504 | 0.08379 | -0.25515 | -0.24431 | 0        |
| 0    | 1         | 0.508 | 0.8375  | -0.25584 | -0.23192 | 0        |
| 0    | 1         | 0.512 | 0.8564  | -0.21048 | -0.21048 | 0        |
| 0    | 1         | 0.516 | 0.8797  | -0.18492 | -0.18001 | 0        |
| 0    | 1         | 0.520 | 0.9069  | -0.14098 | -0.14420 | 0        | 

### 2. A signal excel file that has the signal, peak voltage, and voltage center for each replicate:

| file                    | signal   | peak V | vcenter |
|-------------------------|----------|--------|---------|
| 2024_01_02_cbz00_01.txt | 23.9020  | 1.083  | 1.012   |
| 2024_01_02_cbz15_01.txt | 324.8372 | 1.074  | 1.076   |
| 2024_01_02_cbz15_02.txt | 236.3741 | 1.061  | 1.064   |

### 3. A stats excel file that has the signal, peak voltage, and voltage center for each replicate:

| conc      | average | std   | CV    | T-Statistic | avg peak | std peak |
|-----------|---------|-------|-------|-------------|----------|----------|
| 0.0&mu;M  | 28.9    | 20.11 | 0     | 0           | 1.02     | 0.04     |
| 5.0&mu;M  | 84.11   | 14.19 | 0.169 | 6.34        | 1.06     | 0.01     |
| 10.0&mu;M | 9.80    | 29.8  | 0.206 | 5.19        | 1.07     | 0        |
| 15.0&mu;M | 227.97  | 42.43 | 0.186 | 4.54        | 1.07     | 0        |



# Troubleshooting:

### 1.  Problem: When I try to switch my branch to user-friendly I get the error: 

```
Exception of type 'Microsoft.TeamFoundation.Git.Contracts.GitCheckoutConflictException' was thrown`"
```
This means that the destination branch has more exclusions in .gitignore than the original branch.

**Solution:** in the Git changes, 'ignore' the .suo (or .wsuo) file and then do a force checkout to get to your desired branch.


### 2. Problem: When I am installing the packages, I get an error with `scikit-fda`

This means that you are not using Python 3.9

**Solution:** 
- Uninstall the Python version you have on your computer (make sure it is no longer in PATH). 
- Install Python 3.9 and change your interpreter to the correct version


### 3. Problem: I cannot access the vgrampy github

You need to be added by an admin in order to access the code (currently Noel)

**Solution:** email the admin to get your github account added to the repo