# Harold Mills's utilities (CrossbillDetector is my modification to the original ThrushDetector)
from old_bird_detector_redux_1_1 import CrossbillDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch 

# Used to make directories to save detected calls to, and to remove preexisting dir with the same name 
from os import path, makedirs
from shutil import rmtree
import numpy # write_wave_file takes detections in the form of an nparray

# Own utility to plot bar chart of lengths of detections in sample
from plotter import frequency_bar_plotter

class _Listener:
    
    def __init__(self):
        self.clips = []
        
    def process_clip(self, start_index, length):
        self.clips.append((start_index, length))

def average_length(detections, sample_rate):
    # compute average length in number of samples--only non-outliers (<0.05)
    num_detections = 0
    sample_total = 0
    
    # calculate upper limit of number of samples--higher than 0.15 sec implies detection outlier
    upper_limit = 0.15 * sample_rate
    print(upper_limit)
    
    for detection in detections:
        detection_length = detection[1]
        print(detection_length)
        if detection_length < upper_limit:
            print("hello!")
            num_detections += 1
            sample_total += detection_length
    
    avg_samples = sample_total / num_detections
    print(avg_samples)
    print(avg_samples*sample_rate)
    
    
def make_dir(dir_name, mode):
    ''' 
    Creates a directory if it doesn't already exist. 
    If mode is 1, function recursively deletes everything in preexisting directory.
    '''
    
    if not path.exists(dir_name):
        print("Making directory.")
        makedirs(dir_name)
    elif mode == 1:
        print("Deleting previous directory")
        rmtree(dir_name)
    else: 
        print("Warning: '{}/' already exists. Some contents may be overwritten.".format(dir_name))
    
    
    
def detections_to_files(samples, detections, sample_rate):
    '''
    Uses write_wave_file() from Vesper's audio_file_utils to write audio files given 
    their start time and length in samples.
    
    - samples: a single-channel numpy array of samples
    - detections: a list of tuples (detection_start_time, detection_length) 
      created by _Listener's method, process_clip
    - sample_rate: integer sample rate
    '''
    
    lengths = []
    
    # make a "detections/" folder if it doesn't already exist
    make_dir("detections", 0)
    
    # write clips to "detections/"
    for detection in detections:
        (start, length) = detection
        
        lengths.append(length)
        
        # issue: why are so many of the correct detections 4205 samples long?
        #if length != 4205:
        #   print(length)
        #   continue
        
        # create filename indicating clip start in milliseconds
        start_sec = int(1000 * start/sample_rate)
        filename = "detections/clip{}.wav".format(start_sec)
        
        # create 2D numpy array of detections
        clip = numpy.array([samples[0][start:start+length], samples[1][start:start+length]], numpy.int32)
        
        # warning: will overwrite any clips that already exist
        write_wave_file(filename, clip, sample_rate)
        # print("{} saved".format(filename))
        
    return lengths

def input():
    '''
    Will eventually be used to get user input from command line arg--either a file or a folder
    '''
    
    # Get user input
    # If folder, return [folder path, 'folder']
    # If file, return [file path, 'file']
    # Else, return [FALSE, 0]
    
    return input

    
def channel_counter(samples, filename):
    '''
    Returns a single subarray from `samples`, a two-dimensional array of channels of sound
    read from a .wav file.
    
    Prints different messages depending on how many subarrays are present, and 
    whether the subarrays are identical.
    '''
    if len(samples) > 1:
        if len(samples) == 2: 
            if samples[0].all() == samples[1].all():
                print("Read file {} contains two identical channels.".format(filename))
            else:
                print("Read file {} contains two non-identical channels.".format(filename))
        else:
            print("Multiple channels in input file {}.".format(filename))
        print("Processing first channel.")
        return samples[0]
    elif len(samples) == 1:
        print("Processing single channel in file {}.".format(filename))
        return samples[0]
    else:
        return []
    
def main():
    # get file or folder as user input
    
    #file_path = "smaller_sample.wav"
    file_path = "wav-files/sample.wav"
    #file_path = "Type 2_66622211_flock_16bit.wav"
    
    # read sample file within directory
    (samples, sample_rate) = read_wave_file(file_path)
    type = 2
    
    # this function will be notified
    listener = _Listener()
    
    # get a single channel
    sample = channel_counter(samples, file_path)
    
    # run detection pipeline
    detector = CrossbillDetector(sample_rate, listener, type)
    detector.detect(sample)
    detector.complete_detection()

    # find average length of clips
    #average_length(listener.clips, sample_rate)
    
    # create files and return lengths of files in samples
    lengths = detections_to_files(samples, listener.clips, sample_rate)
    
    # plot lengths of detections
    frequency_bar_plotter(lengths)
    
    print("Files saved in 'detections/'.")

main()