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



class Init_Window(UI_InitWindow):
    def __init__(self):
        super().__init__()

        self.open_count = 0
        self.openMenu.bind("<Button-1>", lambda e: self.open_file())
        self.bttn_run.bind("<Button-1>", lambda e: self.analyze())



    def open_file(self):
        self.dir_path = filedialog.askdirectory(initialdir = BASE_DIR, title='openDir', master=self.init_window)
        if len(self.dir_path) > 40:
            line1 = str(self.dir_path[:40]).rsplit(sep='/', maxsplit=2)[0]
            rest_str = str(self.dir_path).split(line1)[1]
            if len(rest_str) > 40:
                rest_str = rest_str[-40:]
                if '/' in rest_str:
                    self.import_label.config(text=f'{line1}/...\n/{rest_str[-40:].split(sep="/", maxsplit=1)[1]}')
                else:
                    self.import_label.config(text=f'{line1}/...\n{rest_str[-40:]}')
            else:
                self.import_label.config(text=f'{line1}/...\n/{rest_str.split(sep="/", maxsplit=1)[1]}')
        else:
            self.import_label.config(text=self.dir_path)
        self.open_count =+ 1

    def check_input(self, input_dict):
        if len(input_dict['file_paths']) < 1:
            return False
        elif isinstance(input_dict['smoothing_bw'], float) == False:
            return False
        elif isinstance(input_dict['stiffness'], float) == False:
            return False
        elif isinstance(input_dict['v_start'], str) == False:
            return False
        elif isinstance(input_dict['pv_min'], float) == False:
            return False
        elif isinstance(input_dict['pv_max'], float) == False:
            return False
        else:
            return True


    # Function to run analysis
    def analyze(self):
        if self.sprt_cond.get():
            # Separate files into folders based on sheet number
            file_paths = os.listdir(self.dir_path)
            new_file_paths = []
            for path in file_paths:
                path = path.strip()
                if not os.path.isdir(os.path.join(self.dir_path, path)):
                    continue
                else:
                    path = os.path.join(self.dir_path, path)
            
                for file in os.listdir(path):
                    if file.endswith(".txt" or ".csv") and "_" in file:
                        parts = file.split("_")
                        if len(parts) > 2:
                            sheet_number = parts[3]
                            new_folder = os.path.join(path, sheet_number)
                            if not os.path.exists(new_folder):
                                os.makedirs(new_folder)
                            shutil.move(os.path.join(path, file), os.path.join(new_folder, file))

                new_file_paths.extend([os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

            file_paths = new_file_paths
        else:
            try:
                if len(self.dir_path) > 0:
                    file_paths = [self.dir_path]
            except:
                messagebox.showerror('error', 'Check your path!')
        
        user_input = {
            'file_paths' : file_paths,
            'toplot' : self.plot_data.get(),
            'sep' : self.sprt_conc.get(),
            'do_log' : self.log_data.get(),
            'peak_feat' : self.peak_ftr.get(),
            'smoothing_bw' : self.smth_var.get(),
            'stiffness' : self.stff_var.get(),
            'vwidth' : self.vwdth_var.get(),
            'type_id' : self.anlt_code.get(),
            'v_start' : self.svltg_var.get(),
            'pv_min' : self.vrange_start_var.get(),
            'pv_max' : self.vrange_end_var.get()
        }
        input_flag = self.check_input(user_input)
        if input_flag == False:
            # raise
            messagebox.showerror('error', 'Check your input!')
            return

        # Run analysis for all conditions
        for path in file_paths:
            # folder_path=path.strip()
            # print(folder_path)

            smth_fig, smth_ax, dtt_fig, dtt_ax = vg.run_folderpath(path, user_input)
        # Rotate dataframe for easier graphing
        if self.trnsfm_data.get():
            for path in file_paths:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.startswith("dataframe") and file.endswith(".xlsx"):
                            file_path = os.path.join(root, file)
                            df = pd.read_excel(file_path)
                            # Pivot the dataframe to achieve the desired structure
                            df_pivot = df.pivot_table(index='V', columns=['conc', 'replicate'], values='I')

                            # Flatten the MultiIndex columns
                            df_pivot.columns = ['_'.join(map(str, col)) for col in df_pivot.columns]

                            # Reset the index to make 'V' a column again
                            df_pivot.reset_index(inplace=True)

                            # Save the transformed dataframe to a new Excel file in the same directory
                            output_file_path = os.path.join(root, 'transformed_dataframe.xlsx')
                            with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                                df_pivot.to_excel(writer, index=False)

        if self.cstm_plot.get():
            smth_cstm = Custom_window(smth_fig, smth_ax, user_input)
            smth_cstm.customUI.protocol("WM_DELETE_WINDOW", lambda: self.on_close(smth_cstm, dtt_fig, dtt_ax, user_input))
        else:
            messagebox.showinfo('Process', 'Done!')

        # # Notify the user of errors
        # except ValueError as e:
        #     messagebox.showerror("Value Error", f"Invalid Analyate Code: {e}")
        #     print(e)
        # except TypeError as e:
        #     messagebox.showerror("Type Error", f"Invalid Start Voltage: {e}")
        #     print(e)

    def on_close(self, smth, fig, ax, user_input):
        smth.customUI.destroy()
        dtt_cstm = Custom_window(fig, ax, user_input)







class Custom_window(UI_custom):
    def __init__(self, fig, ax, user_input):
        super().__init__()

        self.update_labels(ax)
        self.add_param_info(fig, user_input)

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()

        width_px = int(fig.get_size_inches()[0] * fig.dpi)
        height_px = int(fig.get_size_inches()[1] * fig.dpi)
        self.canvas.get_tk_widget().config(width=width_px, height=height_px)
        self.canvas.get_tk_widget().pack()

        self.update_button.config(command=lambda: self.update_plot(ax))
        self.save_button.config(command=lambda: self.save_plot(self.customUI, fig))

    def update_labels(self, ax):
        self.xmin_var.set(ax.get_xlim()[0])
        self.xmax_var.set(ax.get_xlim()[1])
        self.ymin_var.set(ax.get_ylim()[0])
        self.ymax_var.set(ax.get_ylim()[1])

        self.title_var.set(ax.get_title())

    def update_plot(self, ax):
        xmin = self.xmin_var.get()
        xmax = self.xmax_var.get()
        ymin = self.ymin_var.get()
        ymax = self.ymax_var.get()
        axis_font = self.axft_var.get()
        tick_font = self.tckft_var.get()
        title_font = self.ttft_var.get()
        title = self.title_var.get()
        
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        ax.xaxis.label.set_size(axis_font)
        ax.yaxis.label.set_size(axis_font)
        ax.tick_params(axis='both', labelsize=tick_font)

        ax.set_title(title, fontsize=title_font)

        self.canvas.draw_idle()

    def add_param_info(self, fig, user_input):
        fig.set_size_inches(6, 3, forward=True)

        typeid_dict = {'cbz': 'Carbamazepine', 'lmg':'Lamotrigine', 'oxc':'Oxcarbazepine'}
        peak_dict = {1:'Curvature', 2:'Height', 3:'Area'}

        do_log = user_input['do_log']
        peak_feat = peak_dict[user_input['peak_feat']]
        smoothing_bw = user_input['smoothing_bw']
        stiffness = user_input['stiffness']
        vwidth = user_input['vwidth']
        analyte = typeid_dict[user_input['type_id']]
        v_start = user_input['v_start']
        pv_min = user_input['pv_min']
        pv_max = user_input['pv_max']

        fig.subplots_adjust(left=0.1, right=0.65)
        fig.text(0.7, 0.8, f'Analyte: {analyte}')
        fig.text(0.7, 0.7, f'log: {do_log}')
        fig.text(0.7, 0.65, f'Peak feature: {peak_feat}')
        fig.text(0.7, 0.55, f'Smoothing: {smoothing_bw}')
        fig.text(0.7, 0.5, f'Stiffness: {stiffness}')
        fig.text(0.7, 0.45, f'V width: {vwidth}')
        fig.text(0.7, 0.4, f'start V: {v_start}')
        fig.text(0.7, 0.3, f'Peak voltage range:')
        fig.text(0.7, 0.25, f'{pv_min} - {pv_max}')

    def save_plot(self, root_tk, original_canvas):
        file_path = filedialog.asksaveasfilename(initialdir=BASE_DIR, title="Save Image", filetypes=[("pdf", "*.pdf"),
                                                                                                    ("jpg", ("*.jpg", "*.jpge", "*.jpe", "*.jfif")), ("png", "*.png")],
                                                defaultextension=".png", parent=root_tk)
        
        if file_path == "":
            return

        try:
            original_canvas.savefig(file_path)
            # plt.close(original_canvas)
            messagebox.showinfo("Success", "Save completed.", parent=root_tk)
        except:
            messagebox.showerror("Error", "Save not completed.", parent=root_tk)



    

        



if __name__ == '__main__':
    import_window = Init_Window()
    import_window.init_window.mainloop()