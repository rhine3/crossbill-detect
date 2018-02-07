'''
application.py
by Tessa Rhinehart

A Python3 GUI for inspecting spectrograms
'''

import matplotlib
matplotlib.use('TkAgg')

### Imports ###
# GUI: TkInterface
import tkinter as Tk
import tkinter.filedialog as fd

# Plotting MPL figures with tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

# Default mpl key bindings
from matplotlib.backend_bases import key_press_handler

# Own utils for creating and saving spectrograms and saving wave files
from spectrogram_utils import make_spectrogram, save_spectrogram

# File inspection
from os import listdir
from os.path import splitext

    
### Classes ###
class Application:

    def __init__(self, master=None):
        self.master = master
        self.position = 0
        self.files = []
        
        # Create self.frame with buttons
        self.frame = Tk.Frame()
        self.create_buttons()
        
        # Create self.canvas for plotting
        self.create_canvas()
        self.canvas.mpl_connect('key_press_event',
            lambda event: self.on_key_event(event, self.canvas))
        self.draw_example_fig()
        
    
    def create_buttons(self):        
        quitbutton = Tk.Button(self.frame, text="Quit", command=self.frame.quit)
        quitbutton.pack(side='left')
        
        examplebutton = Tk.Button(self.frame, text="Example", 
            command=self.draw_example_fig)
        examplebutton.pack(side='left')
        
        filebutton = Tk.Button(self.frame, text="Open File",
            command=self.load_file)
        filebutton.pack(side='left')
        
        folderbutton = Tk.Button(self.frame, text="Open Folder", 
            command=self.load_folder)
        folderbutton.pack(side='left')
        
        settingsbutton = Tk.Button(self.frame, text="Settings",
            command=self.set_settings)
        settingsbutton.pack(side='left')
        
        self.frame.pack() # make Frame visible
    
    def create_canvas(self):
        self.fig = Figure(dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        #self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    
    def draw_example_fig(self):
        '''Draw an example figure to test drawing functionality'''
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)    
        path = "C:/Users/tessa/drive/red-crossbills/crossbill-detect/detections/smaller_sample_2936ms.wav"
        self.fig = make_spectrogram(path, self.fig, self.ax)
        self.fig.canvas.draw()
        
    def draw_speck(self, path):
        '''Draw the spectrogram of the wav file at path'''
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.fig = make_spectrogram(path, self.fig, self.ax)
        self.fig.canvas.draw()
    
    def load_file(self):
        '''Open dialog to load & view file'''
        filename = fd.askopenfilename(filetypes=(("WAV files","*.wav"),
            ("all files","*.*")))
        # assert 16 bit, handle "cancel," etc.
        self.draw_speck(filename)
        
    def load_folder(self):
        '''Open dialog to load & view folder, and display first image'''
        dirname = fd.askdirectory()
        self.position = 0
        self.files = []
        
        # handle "cancel"
        
        # Fill self.files with list of wav files
        directory_list = listdir(dirname)
        for path in directory_list:
            name, ext = splitext(path)
            if ext == '.wav': self.files.append(dirname+'/'+path) 
        
        # Draw spectrogram from 
        self.draw_speck(self.files[0])
        
    def load_next_file(self):
        '''Increments position and moves to next file in self.files'''
        self.position += 1
        if self.position < len(self.files):
            filename = self.files[self.position]
            print("Loading {}".format(filename))
            self.draw_speck(filename)
        else:
            print("No more files to load")
    
    def set_settings(self):
        print("Nice!")
        return
    
    def next_file(self):
        # need to implement
        self.position += 1
    
    def on_key_event(self, event, canvas):
        '''Handles keypresses:
        n - display next spectrogram in folder
        1, 2, ... - move to correct folder and display next spectrogram'''
        self.frame.focus_set()
        self.frame.bind("<n>", lambda event: self.load_next_file())
        self.frame.bind("<q>", lambda event: self.frame.quit())
        return
    
### Scripts ###   
def main():
    root = Tk.Tk() # root window
    root.wm_title("Specky")
    root.geometry("300x400+500+200") # dimensions & position
    
    appy = Application(root)
    root.mainloop()
    
    
main()