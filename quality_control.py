'''
This program will create a user interface for performing quality control on spectrograms.
'''

# For creating a spectrogram
from scipy import signal
import matplotlib.pyplot as plt
from audio_file_utils import read_wave_file

def generate_spectrogram():
    '''
    Generate an interpretable image from a single-channel wav file.
    '''
    
    (samples, sample_rate) = read_wave_file(filename)
    assert len(samples) == 1 # audio file must be single-channel
    
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    
    plt.imshow(spectogram)
    plt.pcolormesh(times, frequencies, spectogram)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
    
    return

def main():
    
    # Generate image
    # Handle user responses: Is it a crossbill? What type? Multiple calls?