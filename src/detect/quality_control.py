'''
quality_control.py

A user interface for performing quality control on audio files.
'''

# For creating a spectrogram
from scipy import signal
import matplotlib.pyplot as plt
from audio_file_utils import read_wave_file

def generate_spectrogram(filename):
    '''
    filename: path to a .wav file
    
    returns a spectrogram of a .wav file
    '''
    # read wave file
    (samples, sample_rate) = read_wave_file(filename)
    samples = samples[0]
    

    spectrum, freqs, t, im = plt.specgram(
        samples,
        window = window_hann,
        Fs = sample_rate,
        cmap = 'gray_r',
    )
    
    #plt.ylabel('Frequency (Hz)')
    #plt.xlabel('Time (s)')
    plt.gca().set_ylim([0, 10000])
    plt.show()
    
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
    filename = "detections/clip2693.wav"
    # Generate image
    generate_spectrogram(filename)
    # Handle user responses: Is it a crossbill? What type? Multiple calls?

main()