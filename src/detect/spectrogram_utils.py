'''
quality_control.py

A GUI for performing quality control on audio files.
'''

# For creating a spectrogram
from scipy import signal
import matplotlib.pyplot as plt
from audio_file_utils import read_wave_file

# For finding filename within path
from ntpath import basename 

# For GUI (?)

    
def main():
    
    # make "accepted" folder
    # make "rejected" folder
    # open up a window
    # for all files in folder:
    #   show spectrogram
    #   yes or no?
    #       if yes,
    #           move file and spectrogram to new folder
    #       if no,
    filename = "C:/Users/tessa/drive/red-crossbills/crossbill-detect/detections/clip2936.wav"
    # Generate image
    save_spectrogram(filename, 'C:/Users/tessa/drive/red-crossbills/crossbill-detect/')
    #test_spec_settings(filename)
    # Handle user responses: Is it a crossbill? What type? Multiple calls?

def save_spectrogram(origin_file, destination_path):
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
    
    # Create descriptive filename
    wav_filename = basename(origin_file)
    filename = wav_filename.replace('.wav','')
    name = destination_path+filename+".png"
    
    # Remove axis ticks/labels and remove whitespace
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)   
    
    plt.savefig(name)
    

    
def test_spec_settings(filename):
    '''
    filename: path to a .wav file
    
    Allows visual inspection of several combinations of spectrograms produced 
    by combinations of settings for block size (NFFT) and padding (pad_to)
    
    Best settings seem to be (NFFT, pad_to) = (450, 512)
    '''
    # read wave file
    (samples, sample_rate) = read_wave_file(filename)
    samples = samples[0]
    
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

    
main()