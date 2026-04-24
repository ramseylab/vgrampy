from tkinter import ttk
import tkinter as tk

from commonGUI import Font, resize_by_resolution



class UI_InitWindow():
    def __init__(self):
        self.init_window = tk.Tk()
        self.init_window.title("Vgrampy")
        self.init_window.attributes('-topmost', True)
        self.init_window.bind("<Button-1>", self.remove_topmost)
        geometry = resize_by_resolution(self.init_window, 400, 500, 50, 50)
        self.init_window.geometry(geometry)
        self.init_window.minsize(350, 400)

        fonts = Font()

        ## import section
        # set background
        self.import_frame = tk.Frame(self.init_window, bg = "#FFFFFF")
        self.import_frame.place(relx=0, rely=0, relheight=0.1, relwidth=1.0)
        # import button
        self.openMenu = tk.Button(self.init_window, compound="c", font=fonts.medium, text='Import folder', highlightbackground='#FFFFFF')
        self.openMenu.place(relx=0.01, rely=0.01, relwidth=0.25, relheight=0.08)
        # show imported directory path
        self.import_label = tk.Label(self.init_window, text='directory path', foreground="black", background="#FFFFFF", font=fonts.medium)
        self.import_label.place(relx=0.26, rely=0.01, relheight=0.08)


        ## checkbox options
        self.plot_data = tk.BooleanVar(self.init_window, value=True)
        self.check_plot = tk.Checkbutton(self.init_window, text="Plot data", font=fonts.medium, variable=self.plot_data, onvalue=True, offvalue=False)
        self.check_plot.place(relx=0.02, rely=0.12)

        self.trnsfm_data = tk.BooleanVar(self.init_window, value=True)
        self.check_trnsfm = tk.Checkbutton(self.init_window, text="Transform data", font=fonts.medium, variable=self.trnsfm_data, onvalue=True, offvalue=False)
        self.check_trnsfm.place(relx=0.51, rely=0.12)

        self.sprt_conc = tk.BooleanVar(self.init_window, value=False)
        self.check_conc = tk.Checkbutton(self.init_window, text="Seperate Concentrations", font=fonts.medium, variable=self.sprt_conc, onvalue=True, offvalue=False, command=self.disable_custom)
        self.check_conc.place(relx=0.02, rely=0.17)

        self.sprt_cond = tk.BooleanVar(self.init_window, value=False)
        self.check_cond = tk.Checkbutton(self.init_window, text="Seperate Conditions", font=fonts.medium, variable=self.sprt_cond, onvalue=True, offvalue=False, command=self.disable_custom)
        self.check_cond.place(relx=0.51, rely=0.17)

        self.cstm_plot = tk.BooleanVar(self.init_window, value=False)
        self.check_cstm = tk.Checkbutton(self.init_window, text="Customize Plot", font=fonts.medium, variable=self.cstm_plot, onvalue=True, offvalue=False)
        self.check_cstm.place(relx=0.02, rely=0.22)

        ## analysis options
        # set background
        self.anl_frame = tk.Frame(self.init_window, bg = "#FFFFFF")
        self.anl_frame.place(relx=0, rely=0.3, relheight=0.15, relwidth=1.0)

        self.log_lbl = tk.Label(self.init_window, text="Do log input?", foreground="black", background="#FFFFFF", font=fonts.medium)
        self.log_lbl.place(relx=0.02, rely=0.32)
        self.log_data = tk.BooleanVar(self.init_window); self.log_data.set(True)
        self.radio_log_yes = tk.Radiobutton(self.init_window, text="Yes", background="#FFFFFF", font=fonts.medium, variable=self.log_data, value=True)
        self.radio_log_yes.place(relx=0.27, rely=0.32)
        self.radio_log_no = tk.Radiobutton(self.init_window, text="No", background="#FFFFFF", font=fonts.medium, variable=self.log_data, value=False)
        self.radio_log_no.place(relx=0.42, rely=0.32)

        self.pk_lbl = tk.Label(self.init_window, text="Peak Feature", foreground="black", background="#FFFFFF", font=fonts.medium)
        self.pk_lbl.place(relx=0.02, rely=0.37)
        self.peak_ftr = tk.IntVar(self.init_window); self.peak_ftr.set(3)
        self.radio_area = tk.Radiobutton(self.init_window, text="Area", background="#FFFFFF", font=fonts.medium, variable=self.peak_ftr, value=3)
        self.radio_area.place(relx=0.27, rely=0.37)
        self.radio_cvtr = tk.Radiobutton(self.init_window, text="Curvature", background="#FFFFFF", font=fonts.medium, variable=self.peak_ftr, value=1)
        self.radio_cvtr.place(relx=0.44, rely=0.37)
        self.radio_height = tk.Radiobutton(self.init_window, text="Height", background="#FFFFFF", font=fonts.medium, variable=self.peak_ftr, value=2)
        self.radio_height.place(relx=0.68, rely=0.37)

        self.smth_lbl = tk.Label(self.init_window, text="Smoothing", foreground="black", font=fonts.medium)
        self.smth_lbl.place(relx=0.02, rely=0.47)
        self.smth_var = tk.DoubleVar(self.init_window, value=0.006)
        self.smth_entry = tk.Entry(self.init_window, textvariable=self.smth_var, width=8)
        self.smth_entry.place(relx=0.27, rely=0.47)

        self.stff_lbl = tk.Label(self.init_window, text="Stiffness", foreground="black", font=fonts.medium)
        self.stff_lbl.place(relx=0.52, rely=0.47)
        self.stff_var = tk.DoubleVar(self.init_window); self.stff_var.set(0.0)
        self.stff_entry = tk.Entry(self.init_window, textvariable=self.stff_var, width=8)
        self.stff_entry.place(relx=0.72, rely=0.47)

        self.svltg_lbl = tk.Label(self.init_window, text="Start Voltage", foreground="black", font=fonts.medium)
        self.svltg_lbl.place(relx=0.02, rely=0.52)
        self.svltg_var = tk.StringVar(self.init_window); self.svltg_var.set("0.852")
        self.svltg_entry = tk.Entry(self.init_window, textvariable=self.svltg_var, width=8)
        self.svltg_entry.place(relx=0.27, rely=0.52)

        self.vwdth_lbl = tk.Label(self.init_window, text="Vwidth", foreground="black", font=fonts.medium)
        self.vwdth_lbl.place(relx=0.52, rely=0.52)
        self.vwdth_var = tk.DoubleVar(self.init_window); self.vwdth_var.set(0.15)
        self.vwdth_entry = tk.Entry(self.init_window, textvariable=self.vwdth_var, width=8)
        self.vwdth_entry.place(relx=0.72, rely=0.52)

        self.pvltg_lbl = tk.Label(self.init_window, text="Peak Voltage Range", foreground="black", font=fonts.medium)
        self.pvltg_lbl.place(relx=0.02, rely=0.6)
        self.vrange_start_lbl = tk.Label(self.init_window, text="Start", foreground="black", font=fonts.medium)
        self.vrange_start_lbl.place(relx=0.02, rely=0.65)
        self.vrange_start_var = tk.DoubleVar(self.init_window); self.vrange_start_var.set(1.0)
        self.vrange_start_entry = tk.Entry(self.init_window, textvariable=self.vrange_start_var, width=8)
        self.vrange_start_entry.place(relx=0.27, rely=0.65)
        self.vrange_end_lbl = tk.Label(self.init_window, text="End", foreground="black", font=fonts.medium)
        self.vrange_end_lbl.place(relx=0.52, rely=0.65)
        self.vrange_end_var = tk.DoubleVar(self.init_window); self.vrange_end_var.set(1.1)
        self.vrange_end_entry = tk.Entry(self.init_window, textvariable=self.vrange_end_var, width=8)
        self.vrange_end_entry.place(relx=0.72, rely=0.65)

        self.anlt_lbl = tk.Label(self.init_window, text="Analyte", foreground="black", font=fonts.medium)
        self.anlt_lbl.place(relx=0.02, rely=0.73)
        self.anlt_code = tk.StringVar(self.init_window); self.anlt_code.set('cbz')
        self.radio_area = tk.Radiobutton(self.init_window, text="Carbamazepine", font=fonts.medium, variable=self.anlt_code, value='cbz', command=self.update_params)
        self.radio_area.place(relx=0.2, rely=0.73)
        self.radio_cvtr = tk.Radiobutton(self.init_window, text="Lamotrigine", font=fonts.medium, variable=self.anlt_code, value='lmg', command=self.update_params)
        self.radio_cvtr.place(relx=0.55, rely=0.73)
        self.radio_height = tk.Radiobutton(self.init_window, text="Oxcarbazepine", font=fonts.medium, variable=self.anlt_code, value='oxc', command=self.update_params)
        self.radio_height.place(relx=0.2, rely=0.78)
        # self.radio_height = tk.Radiobutton(self.init_window, text="Others", font=fonts.medium, variable=self.anlt_code, value='')
        # self.radio_height.place(relx=0.55, rely=0.78)

        self.bttn_run = tk.Button(self.init_window, compound="c", font=fonts.large_bold, text='Run Analysis', highlightbackground='#0047AB', highlightcolor='#0047AB', bg='#0047AB', activebackground='#0047AB')
        self.bttn_run.place(relx=0.1, rely=0.9, relwidth=0.8, relheight=0.08)
    

    def remove_topmost(self, event=None):
        self.init_window.attributes('-topmost', False)
        
    def update_params(self):
        if self.anlt_code.get() == 'cbz':
            self.svltg_var.set('0.852')
            self.vrange_start_var.set(1.0)
            self.vrange_end_var.set(1.1)
        elif self.anlt_code.get() == 'lmg':
            self.svltg_var.set('0.852')
            self.vrange_start_var.set(1.24)
            self.vrange_end_var.set(1.4)
        elif self.anlt_code.get() == 'oxc':
            self.svltg_var.set('0.952')
            self.vrange_start_var.set(1.24)
            self.vrange_end_var.set(1.4)
        else:
            pass

    def disable_custom(self):
        if self.sprt_cond.get() | self.sprt_conc.get():
            self.check_cstm.config(state=tk.DISABLED)
            self.cstm_plot.set(False)
        else:
            self.check_cstm.config(state=tk.ACTIVE)


if __name__ == "__main__":
    app = UI_InitWindow()
    app.init_window.mainloop()