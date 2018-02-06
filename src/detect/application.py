import matplotlib
matplotlib.use('TkAgg')

### Imports ###
# For plotting MPL figures with tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

# Implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

# For creating and saving spectrograms and saving wave files
from spectrogram_utils import make_spectrogram, save_spectrogram

# Import correct version of Tkinter depending on Python version
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

### Scripts ###    
def interface():
    root = Tk.Tk()
    root.wm_title("Embedding in TK")

    # Create figure
    fig = Figure(figsize=(5, 4), dpi=100)

    # In the figure, create and return an Axes at index 1 of a 1x1 grid
    ax = fig.add_subplot(111)

    # Make example figure
    clip_path = "C:/Users/tessa/drive/red-crossbills/crossbill-detect/detections/smaller_sample_2936ms.wav"
    fig = make_spectrogram(clip_path, fig, ax)

    # Create a tk.DrawingArea
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.show()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    # Add toolbar
    #toolbar = NavigationToolbar2TkAgg(canvas, root)
    #toolbar.update()
    
    # Implement key press functionality
    canvas.mpl_connect('key_press_event', 
        lambda event: on_key_event(event, canvas, toolbar))
    
    # Implement quit button functionality
    button = Tk.Button(master=root, text='Quit', 
        command=lambda: _quit(root))
    button.pack(side=Tk.BOTTOM)

    Tk.mainloop()
    # If you put root.destroy() here, it will cause an error if
    # the window is closed with the window manager.


def on_key_event(event, canvas, toolbar):
    print('you pressed %s' % event.key)
    
    # Implement default bindings (e.g. s = save)
    #key_press_handler(event, canvas, toolbar)




def _quit(root):
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

interface()