'''
spectrogram_utils.py
by Tessa Rhinehart

Utilities for creating and exporting spectrograms.
'''

### Imports ###
from matplotlib.figure import Figure

# For finding filename within path
from ntpath import basename 

# For reading samples from wave files
from audio_file_utils import read_wave_file

### Scripts ###
def make_spectrogram(origin_file, figure, axes, freq=20000, points=450, pad=512):
    '''Updates the data of a given axis with a spectrogram 
    generated from origin_file'''

    # Read wave file
    (samples, sample_rate) = read_wave_file(origin_file)
    samples = samples[0]

    spectrum, freqs, t, im = axes.specgram(
        samples,
        Fs = freq,
        NFFT = points, # window size
        pad_to = pad,
        cmap = 'gray_r', # gray color map
    )

    # View frequencies between 0 and 10 kHz
    axes.set_ylim(0, 2000)    

    # Remove axis ticks/labels and remove whitespace
    figure.subplots_adjust(left=0, right=1, bottom=0, top=1)   
    
    return figure
      
def save_spectrogram(origin_file, destination_path, fig):
    '''Saves a figure with a similar name as its .wav origin file
    e.g. if the origin path is: data/clip3320.wav
    the spectrogram path is: destination_path/clip3320.png)'''
    
    # Create descriptive filename & append desired path
    filename = basename(origin_file).replace('.wav', '')
    file_path = destination_path+filename+".png"
    
    # Save fig to specified path
    fig.savefig(file_path)