from tkinter import ttk
import tkinter as tk

from commonGUI import Font, resize_by_resolution



class UI_custom():
    def __init__(self):
        self.customUI = tk.Toplevel()
        self.customUI.title("Vgrampy")

        geometry = resize_by_resolution(self.customUI, 600, 500, 800, 100)
        self.customUI.geometry(geometry)
        # self.customUI.minsize(600, 600)

        fonts = Font()
        self.title = tk.Label(self.customUI, font=fonts.large_bold)
        self.title.place(relx=0.3, rely=0.015)

        self.plot_frame = tk.LabelFrame(self.customUI, labelanchor='n', font = fonts.small, relief="solid", bd=1)
        self.plot_frame.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.61)

        self.custom_frame = tk.LabelFrame(self.customUI, labelanchor='n', font = fonts.small, relief="solid", bd=1)
        self.custom_frame.place(relx=0.02, rely=0.66, relwidth=0.96, relheight=0.3)

        self.xmin_lbl = tk.Label(self.customUI, text="X-axis min", foreground="black", font=fonts.medium)
        self.xmin_lbl.place(relx=0.04, rely=0.68)
        self.xmin_var = tk.DoubleVar(self.customUI)
        self.xmin_entry = tk.Entry(self.customUI, textvariable=self.xmin_var, width=8)
        self.xmin_entry.place(relx=0.18, rely=0.68)

        self.xmax_lbl = tk.Label(self.customUI, text="X-axis max", foreground="black", font=fonts.medium)
        self.xmax_lbl.place(relx=0.04, rely=0.73)
        self.xmax_var = tk.DoubleVar(self.customUI)
        self.xmax_entry = tk.Entry(self.customUI, textvariable=self.xmax_var, width=8)
        self.xmax_entry.place(relx=0.18, rely=0.73)

        self.ymin_lbl = tk.Label(self.customUI, text="Y-axis min", foreground="black", font=fonts.medium)
        self.ymin_lbl.place(relx=0.36, rely=0.68)
        self.ymin_var = tk.DoubleVar(self.customUI)
        self.ymin_entry = tk.Entry(self.customUI, textvariable=self.ymin_var, width=8)
        self.ymin_entry.place(relx=0.5, rely=0.68)

        self.ymax_lbl = tk.Label(self.customUI, text="Y-axis max", foreground="black", font=fonts.medium)
        self.ymax_lbl.place(relx=0.36, rely=0.73)
        self.ymax_var = tk.DoubleVar(self.customUI)
        self.ymax_entry = tk.Entry(self.customUI, textvariable=self.ymax_var, width=8)
        self.ymax_entry.place(relx=0.5, rely=0.73)

        self.axft_lbl = tk.Label(self.customUI, text="Axis font", foreground="black", font=fonts.medium)
        self.axft_lbl.place(relx=0.68, rely=0.68)
        self.axft_var = tk.DoubleVar(self.customUI, value=10)
        self.axft_entry = tk.Entry(self.customUI, textvariable=self.axft_var, width=8)
        self.axft_entry.place(relx=0.82, rely=0.68)

        self.tckft_lbl = tk.Label(self.customUI, text="Tick font", foreground="black", font=fonts.medium)
        self.tckft_lbl.place(relx=0.68, rely=0.73)
        self.tckft_var = tk.DoubleVar(self.customUI, value=10)
        self.tckft_entry = tk.Entry(self.customUI, textvariable=self.tckft_var, width=8)
        self.tckft_entry.place(relx=0.82, rely=0.73)

        self.title_lbl = tk.Label(self.customUI, text="Title", foreground="black", font=fonts.medium)
        self.title_lbl.place(relx=0.04, rely=0.78)
        self.title_var = tk.StringVar(self.customUI)
        self.title_entry = tk.Entry(self.customUI, textvariable=self.title_var, width=35)
        self.title_entry.place(relx=0.095, rely=0.78)

        self.ttft_lbl = tk.Label(self.customUI, text="Title font", foreground="black", font=fonts.medium)
        self.ttft_lbl.place(relx=0.68, rely=0.78)
        self.ttft_var = tk.DoubleVar(self.customUI, value=12)
        self.ttft_entry = tk.Entry(self.customUI, textvariable=self.ttft_var, width=8)
        self.ttft_entry.place(relx=0.82, rely=0.78)

        self.update_button = tk.Button(self.customUI, text="Update", font=fonts.medium)
        self.update_button.place(relx=0.82, rely=0.85, relwidth=0.14, relheight=0.05)

        self.save_button = tk.Button(self.customUI, text="Save Plot", font=fonts.medium)
        self.save_button.place(relx=0.82, rely=0.9, relwidth=0.14, relheight=0.05)    



    def remove_topmost(self, event=None):
        self.customUI.attributes('-topmost', False)



if __name__ == "__main__":
    app = UI_custom()
    app.customUI.mainloop()