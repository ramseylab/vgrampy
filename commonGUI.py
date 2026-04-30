import sys


class Font():
    def __init__(self):
        os_type = sys.platform

        if os_type == "win32":
            self.small = ("Arial", '9')
            self.medium = ("Arial",'11')
            self.medium_bold = ("Arial", '11', "bold")
            self.medium_italic = ("Arial",'11', "italic")
            self.large = ("Arial", '13')
            self.large_bold = ("Arial", '13', "bold")
            self.large_italic = ("Arial",'13', "italic")
            self.large_bold_italic = ("Arial",'13', "bold italic")
            self.background = "#F0F0F0"

        elif os_type == "darwin":
            self.small = ("Arial", '12')
            self.medium = ("Arial",'14')
            self.medium_bold = ("Arial", '14', "bold")
            self.medium_italic = ("Arial", '14', "italic")
            self.large = ("Arial", '16')
            self.large_bold = ("Arial", '16', "bold")
            self.large_italic = ("Arial",'16', "italic")
            self.large_bold_italic = ("Arial",'16', "bold italic")
            self.background = "#ECECEC"
            

# original means the size of activated window (Windows: 1920x1080)
# display means the size of device display
def resize_by_resolution(root_tk, original_width, original_height, app_x=None, app_y=None):
    display_width = root_tk.winfo_screenwidth()
    display_height = root_tk.winfo_screenheight()

    if app_x == None and app_y == None:
        app_x = (display_width - original_width) // 2
        app_y = (display_height - original_height) // 2

    geometry = '{}x{}+{}+{}'.format(original_width, original_height, app_x, app_y)

    return geometry
