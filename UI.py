# This program sets up a user freindly UI for vgrampy
import os
import shutil
import groupvg2 as vg
import pandas as pd
import tkinter
import tkinter.messagebox
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Vgram Analysis")
        self.geometry("430x520")
        self.resizable(False, False)

        # Override the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # configure grid layout (3x3)
        #self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=0)
        #self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure((0, 1), weight=0)

        # Text input for file path(s)
        self.file_path_input = ctk.CTkTextbox(self, height=100)
        self.file_path_input.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="nsew")

        # Checkboxes for plot and sep plot
        self.cb_frame = ctk.CTkFrame(self)
        self.cb_frame.grid(row=1, column=0, columnspan=2, padx=(20,20), pady=(10,10), sticky="nsew")
        self.plot_cb_var = ctk.BooleanVar()
        self.plot_cb = ctk.CTkCheckBox(master=self.cb_frame, text="Plot Data", command=self.toggle_sep_plot, variable=self.plot_cb_var, onvalue=True, offvalue=False)
        self.plot_cb.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="nw")
        self.sep_plot_cb_var = ctk.BooleanVar()
        self.sep_plot_cb = ctk.CTkCheckBox(master=self.cb_frame, text="Separate Concentrations", variable=self.sep_plot_cb_var, onvalue=True, offvalue=False)
        self.sep_plot_cb.grid(row=1, column=0, pady=10, padx=20, sticky="nw")
        self.tran_cb_var = ctk.BooleanVar()
        self.tran_cb = ctk.CTkCheckBox(master=self.cb_frame, text="Transform Data", variable=self.tran_cb_var, onvalue=True, offvalue=False)
        self.tran_cb.grid(row=0, column=1, pady=(20, 10), padx=20, sticky="n")
        self.sep_sheet_cb_var = ctk.BooleanVar()
        self.sep_sheet_cb = ctk.CTkCheckBox(master=self.cb_frame, text="Separate Conditions", variable=self.sep_sheet_cb_var, onvalue=True, offvalue=False)
        self.sep_sheet_cb.grid(row=1, column=1, pady=10, padx=20, sticky="n")

        # Label for spacing
        #self.label = ctk.CTkLabel(master=self.cb_frame, text="", width=100)
        #self.label.grid(row=0, column=1, padx=20, pady=10)

        # Option boxes and text inputs
        self.ob_frame = ctk.CTkFrame(self)
        self.ob_frame.grid(row=2, column=0, columnspan=2, padx=(20, 20), pady=(10, 20), sticky="nsew")
        self.ob1_label = ctk.CTkLabel(master=self.ob_frame, text="Do log input?")
        self.ob1_label.grid(row=0, column=0, padx=(10, 140), pady=(5, 0), sticky="sw")
        self.ob1 = ctk.CTkComboBox(master=self.ob_frame, values=["Yes", "No"])
        self.ob1.grid(row=1, column=0, pady=(0,5), padx=(10, 48), sticky="nw")
        self.ob2_label = ctk.CTkLabel(master=self.ob_frame, text="Peak Feature")
        self.ob2_label.grid(row=2, column=0, padx=10, pady=(0), sticky="sw")
        self.ob2 = ctk.CTkComboBox(master=self.ob_frame, values=["Curvature", "Height", "Area"])
        self.ob2.grid(row=3, column=0, pady=(0,5), padx=(10, 48), sticky="nw")
        
        self.ti1_label = ctk.CTkLabel(master=self.ob_frame, text="Smoothing")
        self.ti1_label.grid(row=0, column=1, padx=(10, 10), pady=(5, 0), sticky="se")
        self.smooth_input = ctk.CTkEntry(master=self.ob_frame, placeholder_text="Text input")
        self.smooth_input.grid(row=1, column=1, pady=(0,5), padx=(10, 10), sticky="ne")
        self.ti2_label = ctk.CTkLabel(master=self.ob_frame, text="Stiffness")
        self.ti2_label.grid(row=2, column=1, padx=(10, 10), pady=(0), sticky="se")
        self.stiff_input = ctk.CTkEntry(master=self.ob_frame, placeholder_text="Text input")
        self.stiff_input.grid(row=3, column=1, pady=(0,5), padx=(10, 10), sticky="ne")
        self.ti3_label = ctk.CTkLabel(master=self.ob_frame, text="Vwidth")
        self.ti3_label.grid(row=4, column=1, padx=(10, 10), pady=(0), sticky="se")
        self.vwidth_input = ctk.CTkEntry(master=self.ob_frame, placeholder_text="Text input")
        self.vwidth_input.grid(row=5, column=1, pady=(0,10), padx=(10, 10), sticky="ne")

        #self.op_frame = ctk.CTkFrame(self)
        #self.op_frame.grid(row=2, column=1, columnspan=2, padx=(10, 20), pady=(10, 20), sticky="nsew")

        # Button at the bottom
        self.submit_button = ctk.CTkButton(self, text="Run Analysis", command=self.analyze)
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=(0,10), padx=20, sticky="nsew")

        # set default values
        self.sep_plot_cb.configure(state='disabled')
        self.file_path_input.insert("1.0", 'Enter path to folder(s) containing data, one per line.')
        self.smooth_input.insert("0", '0.006')
        self.stiff_input.insert("0", '0')
        self.vwidth_input.insert("0", "0.15")
        self.ob1.set("Yes")
        self.ob2.set("Area")


    # Function to enable/disable "Sep Plot" checkbox based on "Plot" checkbox state
    def toggle_sep_plot(self):
        if self.plot_cb_var.get():
            self.sep_plot_cb.configure(state='normal')
        else:
            self.sep_plot_cb.deselect()
            self.sep_plot_cb.configure(state='disabled')
    
    def analyze(self):
        try:    
            log_options = {"Yes":True, "No":False}
            peak_options = {"Curvature":1, "Height":2, "Area":3}

            # Get file paths
            file_paths = self.file_path_input.get("1.0", "end").strip().split('\n')

            # Get other parameters
            plot = self.plot_cb_var.get()
            sepplot = self.sep_plot_cb_var.get()
            do_loginput = log_options[self.ob1.get()]
            peak_featinput = peak_options[self.ob2.get()]
            smoothing_bwinput = float(self.smooth_input.get())
            stiffnessinput = float(self.stiff_input.get())
            vwidthinput = float(self.vwidth_input.get())

            if self.sep_sheet_cb_var.get():
                # Separate files into folders based on sheet number
                new_file_paths = []
                for path in file_paths:
                    path = path.strip()
                    if not os.path.isdir(path):
                        continue

                    for file in os.listdir(path):
                        if file.endswith(".txt") and "_" in file:
                            parts = file.split("_")
                            if len(parts) > 2:
                                sheet_number = parts[3]
                                new_folder = os.path.join(path, sheet_number)
                                if not os.path.exists(new_folder):
                                    os.makedirs(new_folder)
                                shutil.move(os.path.join(path, file), os.path.join(new_folder, file))

                    new_file_paths.extend([os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

                file_paths = new_file_paths

            for path in file_paths:
                folder_path=path.strip()
                print(folder_path)
                vg.run_folderpath(
                    folder_path,
                    plot,
                    sepplot,
                    do_loginput,
                    peak_featinput,
                    smoothing_bwinput,
                    stiffnessinput,
                    vwidthinput
                )

            if self.tran_cb_var.get():
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

        except ValueError as e:
            tkinter.messagebox.showerror("Input Error", f"Invalid input: {e}")

    def on_closing(self):
        self.destroy()
        self.quit()


if __name__ == "__main__":
    app = App()
    app.mainloop()