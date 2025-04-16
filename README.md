# vgrampy

  

### Author: Caleb Nejely ( Adapted from Noel Lefevre (Adapted from Steven Ramsey's LDNH README.md)))

### Date: July 1, 2024

  

# Running Packaged `Vgram` Program

  1. Download Vgram setup from latest release
  > **Warning**  
  > This program is not signed by a windows approved certificate because they're expensive, you may have to select run anyway when warned about unknown code.

2. Run the setup program and follow prompts

3. You can now run the Vgram UI!
> Please note that it may take a while to start

# Self Compiling `Vgram`

  > **You Must have Python installed.**
  > Tested and working on 3.9.x, may work on newer versions.

1. Clone the repository
```
git clone https://github.com/chickenmanxl/Vgram_UI.git
cd Vgram_UI
```

2. Install dependencies
- If you only have one version of python installed
	```
	pip install -r requirements.txt
	```
 
3. Build the exe
	```
	pyinstaller Vgram_UI.spec
	```
4. Run!


# Options for `Vgram`:

  

### There are default parameters applied, but you can change them if needed

  

- **Plot Data**: generate automatic plots of the data

- **Seperate Concentrations**: seperate plots based on concentration in the file name

- **Transform Data**: rotates and cleans up the output dataframe for easier work in excel, add an additional output file

- **Seperate Conditions**: seperates data into folder before analysis based on the fourth item in the file name (eg. condition in "YYYY_MM_DD_<Condition (optional)>_<Analyte Code><Concentration>_<Test Number>")

- **Do log input**: log-transform or not (default 'yes')

- **Peak Feature**: peak curvature, height or area (default = peak curvature)

- **Start Voltage**: voltage start point of data (default = 0.852 for carbamazepine, change to 0.952 for oxcarbazepine)

- **Analyate Code**: code for drug of intrest (cbz for carbamazepine, oxc for oxcarbazepine)

- **Smoothing**: amount of smoothing the voltammogram (default = 0.006)

- **Stiffness**: how strictly the spline passes through the data points (default = 0)

- **Vwidth**: voltage width to window out when making the spline (default = 0.15)

- **Peak Voltage Range**: voltage range to look for the peak in (default = 1.0 to 1.1)

  

# Plotting In `Vgram`:

  

#### You can choose whether or not to plot, and whether to separate those plots by concentration

#### The plots saved will be the smoothed and detilted voltammograms

  

# Output Files

  

## There are 3 files created by running the installed program by default

  

The naming convention for each file is: `[filename]_[log or no log]_[smoothing parameter]_[stiffness parameter]_[window width]`

  

For example `dataframe_log_curvature_0.006_0_0.15.xlsx`

  

### 1. A dataframe excel file that has each replicates' data:

  

| conc | replicate | V     | I       | logI     | smoothed | detilted |
|------|-----------|-------|---------|----------|:---------|----------|
| 0    | 1         | 0.504 | 0.08379 | -0.25515 | -0.24431 | 0        |
| 0    | 1         | 0.508 | 0.8375  | -0.25584 | -0.23192 | 0        |
| 0    | 1         | 0.512 | 0.8564  | -0.21048 | -0.21048 | 0        |
| 0    | 1         | 0.516 | 0.8797  | -0.18492 | -0.18001 | 0        |
| 0    | 1         | 0.520 | 0.9069  | -0.14098 | -0.14420 | 0        |

  

### 2. A signal excel file that has the signal, peak voltage, and voltage center for each replicate:

  

| file                    | signal   | peak V | vcenter |
|-------------------------|----------|--------|---------|
| 2024_01_02_cbz00_01.txt | 23.9020  | 1.083  | 1.012   |
| 2024_01_02_cbz15_01.txt | 324.8372 | 1.074  | 1.076   |
| 2024_01_02_cbz15_02.txt | 236.3741 | 1.061  | 1.064   |

  

### 3. A stats excel file that has the signal, peak voltage, and voltage center for each replicate:

  

| conc      | average | std   | CV    | T-Statistic | avg peak | std peak |
|-----------|---------|-------|-------|-------------|----------|----------|
| 0.0&mu;M  | 28.9    | 20.11 | 0     | 0           | 1.02     | 0.04     |
| 5.0&mu;M  | 84.11   | 14.19 | 0.169 | 6.34        | 1.06     | 0.01     |
| 10.0&mu;M | 9.80    | 29.8  | 0.206 | 5.19        | 1.07     | 0        |
| 15.0&mu;M | 227.97  | 42.43 | 0.186 | 4.54        | 1.07     | 0        |
