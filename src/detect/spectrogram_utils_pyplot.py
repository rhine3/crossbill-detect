'''
spectrogram_utils_pyplot.py
by Tessa Rhinehart

Utilities for creating, exporting, and viewing spectrograms using pyplot.
'''

# For creating a spectrogram
from scipy import signal
import matplotlib.pyplot as plt
from audio_file_utils import read_wave_file

# For finding filename within path
from ntpath import basename 
    
def example():
   
   # Example clip
    clip_path = "C:/Users/tessa/drive/red-crossbills/crossbill-detect/detections/smaller_sample_2936ms.wav"
    
    # Generate spectrogram
    figure, axes = make_speck(clip_path)
    
    # Save spectrogram
    destination = 'C:/Users/tessa/drive/red-crossbills/crossbill-detect/'
    save_speck(clip_path, destination, figure)
    
    

def make_speck(origin_file):
    '''Generates a spectrogram from filename (a .wav file) and saves it 
    to a .png file in destination_path. Spectrogram has no whitespace.'''
    
    # read wave file
    (samples, sample_rate) = read_wave_file(origin_file)
    samples = samples[0]
    
    fig, ax = plt.subplots(figsize=(1,1))
    
    spectrum, freqs, t, im = plt.specgram(
        samples,
        Fs = 20000,
        NFFT = 450, # window size
        pad_to = 512,
        cmap = 'gray_r', # gray color map
    )
    
    plt.gca().set_ylim([0, 2000])
    
    # Remove axis ticks/labels and remove whitespace
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)   
    
    return fig, ax 
    
def save_speck(origin_file, destination_path, fig):
    '''Saves a spectrogram with a similar name as its origin file
    e.g. if the origin path is: data/clip3320.wav
    the spectrogram path is: destination_path/clip3320.png)'''
    
    # Create descriptive filename & append desired path
    filename = basename(origin_file).replace('.wav', '')
    file_path = destination_path+filename+".png"
    
    # Save fig to specified path
    fig.savefig(file_path)
    
    
def test_spec_settings(filename):
    '''
    filename: path to a .wav file
    
    Allows visual inspection of several combinations of spectrograms produced 
    by combinations of settings for block size (NFFT) and padding (pad_to)
    
    Best settings seem to be (NFFT, pad_to) = (450, 512)
    '''
    # Read wave file
    (samples, sample_rate) = read_wave_file(filename)
    samples = samples[0]
    
    # Parameters to test
    block_sizes = [400, 450, 512, 600]
    paddings = [400, 512, 600, 1024]
    
    fig, axs = plt.subplots(len(block_sizes), len(paddings),
        figsize=(3*len(block_sizes), 3*len(paddings)), dpi=80, facecolor='w', edgecolor='k')
        
    axs = axs.ravel()
    subplot_num = 1
    
    # Create grid of spectrogram displays
    for block_size in block_sizes:
        for padding in paddings:
            ax = plt.subplot(4, 4, subplot_num)
            ax.set_title("NFFT: {} - PAD: {}".format(block_size, padding))
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            
            spectrum, freqs, t, im = plt.specgram(
                samples,
                Fs = 20000,
                NFFT = block_size, # window size
                pad_to = padding,
                cmap = 'gray_r', # gray color map
            )
            
            plt.gca().set_ylim([0, 2000])
    
            
            subplot_num += 1
   
    plt.show()
