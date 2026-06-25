from tkinter import filedialog, messagebox, BOTH, TOP
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import sys
import os
import shutil
import pandas as pd

from ui_init import UI_InitWindow
import groupvg2 as vg
from ui_custom import UI_custom



os_type = sys.platform

if os_type == "win32":
    os_type = "win"
    BASE_DIR = ""
else:
    os_type = "macOS" 
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])).replace("/main", "", 1) + '/'   # macOS



# Function to run analysis
def analyze(dir_path, smoothing_type, pv_max):

    file_paths = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not file.endswith((".txt", ".csv")) or "_" not in file:
                continue

            parts = file.split("_")
            if len(parts) <= 3:
                continue

            cond = parts[3]
            if cond == root:
                continue
            new_folder = os.path.join(root, cond)

            if new_folder == os.path.dirname(os.path.join(root, file)):
                continue
            
            if not os.path.exists(new_folder):
                os.makedirs(new_folder)
                file_paths.append(new_folder)
            shutil.move(os.path.join(root, file), os.path.join(new_folder, file))
    
    user_input = {
        'file_paths' : file_paths,
        'toplot' : True,
        'sep' : True,
        'do_log' : True,
        'peak_feat' : 3,
        'smoothing_type' : smoothing_type,
        'smoothing_bw' : 0.006,
        'stiffness' : 0.0,
        'vwidth' : 0.15,
        'type_id' : 'cbz',
        'v_start' : '0.852',
        'pv_min' : 1.0,
        'pv_max' : pv_max
    }
    
    # Run analysis for all conditions
    for path in file_paths:
        # folder_path=path.strip()
        # print(folder_path)

        smth_fig, smth_ax, dtt_fig, dtt_ax = vg.run_folderpath(path, user_input)
    # Rotate dataframe for easier graphing
    for path in file_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.startswith("dataframe") and file.endswith(".xlsx"):
                    file_path = os.path.join(root, file)
                    df = pd.read_excel(file_path, sheet_name='dataframe')
                    # Pivot the dataframe to achieve the desired structure
                    df_pivot = df.pivot_table(index='V', columns=['conc', 'replicate'], values='I')

                    # Flatten the MultiIndex columns
                    df_pivot.columns = ['_'.join(map(str, col)) for col in df_pivot.columns]

                    # Reset the index to make 'V' a column again
                    df_pivot.reset_index(inplace=True)

                    # Save the transformed dataframe to a new Excel file in the same directory
                    output_file_path = os.path.join(root, f'transformed_{file}')
                    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                        df_pivot.to_excel(writer, index=False)

    all_signal = pd.DataFrame()
    param_exist = False
    for path in file_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.startswith("signal") and file.endswith(".xlsx"):
                    file_path = os.path.join(root, file)
                    if param_exist == False:
                        vgrampy_param_df = pd.read_excel(file_path, sheet_name='signal', nrows=2)
                        param_exist = True

                    df = pd.read_excel(file_path, sheet_name='signal', skiprows=3, usecols=[0,1,2,3])
                    # print(df)
                    all_signal = pd.concat([all_signal, df])
    all_signal['date'] = all_signal['file'].str[:10]
    all_signal['condition'] = all_signal['file'].str.split('_').str.get(3)
    all_signal['drug_conc'] = all_signal['file'].str.split('_').str.get(4).str.split('cbz').str.get(1)

    if all_signal['drug_conc'].str.contains('p').any():
        all_signal['drug_conc'] = all_signal['drug_conc'].str.replace('p', '.')
    
    all_signal['drug_conc'] = all_signal['drug_conc'].astype(float)

    avg_df = all_signal[['date', 'condition', 'drug_conc', 'signal']].groupby(['date', 'condition', 'drug_conc']).mean().round(4).reset_index()
    avg_df.rename(columns={'signal':'AVG'}, inplace=True)
    std_df = all_signal[['date', 'condition', 'drug_conc', 'signal']].groupby(['date', 'condition', 'drug_conc']).std().round(4).reset_index()
    std_df.rename(columns={'signal':'STD'}, inplace=True)

    stat_df = avg_df.merge(std_df, on=['date', 'condition', 'drug_conc'])
    
    cnt_df = all_signal[['date', 'condition', 'drug_conc', 'signal']].groupby(['date', 'condition', 'drug_conc']).count().reset_index()
    cnt_df.rename(columns={'signal':'count'}, inplace=True)

    stat_df = stat_df.merge(cnt_df, on=['date', 'condition', 'drug_conc'])
    stat_df.insert(0, 'label', stat_df['condition']+'_'+stat_df['drug_conc'].astype(str)+'uM')
    # print(stat_df)

    with pd.ExcelWriter(os.path.join(dir_path, 'integrated_signal.xlsx'), engine='openpyxl') as writer:
        vgrampy_param_df.to_excel(writer, index=False, sheet_name='integrated')
        stat_df.to_excel(writer, index=False, sheet_name='integrated', startrow=3)
        all_signal.to_excel(writer, index=False, sheet_name='integrated', startrow=len(stat_df)+5)
        vg.adjust_column(writer, sheet_name='integrated')
            




if __name__ == '__main__':
    org_dir = 'C:/Users/jeongsu/Downloads/raw_ML_dataset'

    pv_max_str_dict = {1.10:'110', 1.15:'115'}

    pv_max = 1.10

    for smoothing_type in ['None', 'NW', 'SG', 'polynomial']:
        dir_path = f'C:/Users/jeongsu/Downloads/MLdataset_{smoothing_type}'
        if not os.path.exists(dir_path):
            shutil.copytree(org_dir, dir_path)

        analyze(dir_path, smoothing_type, pv_max)