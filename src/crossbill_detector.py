# Harold Mills's utilities (CrossbillDetector and OpenDetector are my modifications)
from old_bird_detector_redux_1_1 import CrossbillDetector, OpenDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch 

# Various ops related to reading in samples and saving detections
from os import makedirs, listdir
from shutil import rmtree
import numpy # write_wave_file takes detections in the form of an nparray

# Own utility to plot bar chart of lengths of detections in sample
from plotter import frequency_bar_plotter

# For validating files/directories and using command line arguments
from argument_parser import is_directory, is_wav_file, input_validation

import logging

class _Listener:
    
    def __init__(self):
        self.clips = []
        
    def process_clip(self, start_index, length):
        self.clips.append((start_index, length))

def average_length(detections, sample_rate):
    '''
    Find average sample length
    '''
    # compute average length in number of samples--only non-outliers (<0.05)
    num_detections = 0
    sample_total = 0
    
    # calculate upper limit of number of samples--higher than 0.15 sec implies detection outlier
    upper_limit = 0.15 * sample_rate
    #print(upper_limit)
    
    for detection in detections:
        detection_length = detection[1]
        #print(detection_length)
        if detection_length < upper_limit:
            #print("detection exceeds determined sample limit")
            num_detections += 1
            sample_total += detection_length
    
    avg_samples = sample_total / num_detections
    #print(avg_samples)
    #print(avg_samples*sample_rate)
    
    
def make_dir(dir_name, mode):
    ''' 
    Creates a directory if it doesn't already exist. 
    If directory does exist:
        - if mode is 0, function doesn't delete previous directory or make a new directory
        - if mode is 1, function recursively deletes everything in preexisting directory
        - if mode is 2, function makes a new directory with a number appended to it
    '''
    
    if not is_directory(dir_name):
        logging.info("Making directory '{}/'".format(dir_name))
        makedirs(dir_name)
    elif mode == 0:
        logging.warning("Warning: '{}/' already exists; some contents may be overwritten".format(dir_name))
    elif mode == 1:
        logging.warning("Warning: deleting preexisting directory '{}'/".format(dir_name))
        rmtree(dir_name)
    else: #mode == 2
        increment = 2
        new_name = dir_name + str(increment)
        while is_directory(new_name):
            increment += 1
            new_name = dir_name + '-' + str(increment)
        dir_name = new_name
        logging.info("Making directory '{}/'".format(dir_name))
        makedirs(dir_name)
    
    return dir_name
    
def detections_to_files(samples, detections, sample_rate, dir_name):
    '''
    Uses write_wave_file() from Vesper's audio_file_utils to write audio files given 
    their start time and length in samples.
    
    - samples: a single-channel numpy array of samples
    - detections: a list of tuples (detection_start_time, detection_length) 
      created by _Listener's method, process_clip
    - sample_rate: integer sample rate
    '''
    
    lengths = []
    
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
        filename = "{}/clip{}.wav".format(dir_name, start_sec)
        
        # create 2D numpy array of detections
        clip = numpy.array([samples[0][start:start+length], samples[1][start:start+length]], numpy.int32)
        
        # warning: will overwrite any clips that already exist
        write_wave_file(filename, clip, sample_rate)
        # print("{} saved".format(filename))
        
    return lengths
    
def channel_counter(samples, filename):
    '''
    Returns the first subarray from `samples`, a two-dimensional array of channels of sound
    read from a .wav file.
    
    Prints different messages depending on how many subarrays are present, and 
    whether the subarrays are identical.
    '''
    if len(samples) > 1:
        if len(samples) == 2: 
            if samples[0].all() == samples[1].all():
                logging.warning("File '{}' contains two identical channels as read".format(filename))
            else:
                logging.warning("File '{}' contains two non-identical channels as read".format(filename))
        else:
            logging.warning("Multiple channels in file '{}' as read".format(filename))
        logging.info("Processing first channel")
        return samples[0]
    elif len(samples) == 1:
        logging.info("Processing single channel in file '{}'".format(filename))
        return samples[0]
    else:
        return []
    
def settings_testing(filename):
    '''
    For trying a whole bunch of different settings. Creates several settings "Bunches"
    to be used by function detect_from_file_test
    '''
    
    settings_group = []
    f0_settings = [800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600]
    OLD_FS = 22050
    
    for i in range(10):
        generated_settings = Bunch(
            name = 'settings' + str(i),
            filter_f0 = f0_settings[i],         # hertz #RECR modification
            filter_f1=4400,                     # hertz #RECR modification
            filter_bw=100,                      # hertz
            filter_duration=100 / OLD_FS,      # seconds
            integration_time=4000 / OLD_FS,    # seconds
            ratio_delay=.02,                    # seconds
            ratio_threshold=1.3,                # dimensionless
            min_duration=.030,                  # seconds #RECR modification
            max_duration=.050,                  # seconds #RECR modification
            initial_padding=1000 / OLD_FS,     # seconds #RECR modification
            suppressor_count_threshold=10,      # clips
            suppressor_period=20                # seconds
        )
        settings_group.append(generated_settings)
    
    for settings in settings_group:
        detect_from_file_test(filename, settings)


def detect_from_file_test(filename, settings):
    '''
    Differs from detect_from_file by using "OpenDetector" which allows
    the user to call the detector with their own settings
    '''
    # read sample file within directory
    (samples, sample_rate) = read_wave_file(filename)
    
    # this function will be notified
    listener = _Listener()
    
    # get a single channel
    sample = channel_counter(samples, filename)
    
    # TEST: run detection pipeline
    detector = OpenDetector(sample_rate, listener, settings)
    detector.detect(sample)
    detector.complete_detection()

    # find average length of clips
    #average_length(listener.clips, sample_rate)
    
    # make a "detections/" folder or similar if it doesn't already exist
    # TEST: add name of settings to directory
    dir_name = make_dir("detections-"+settings.name, 2)
    
    # create files in new folder and return lengths of files in samples
    lengths = detections_to_files(samples, listener.clips, sample_rate, dir_name)
    
    #  some final information
    #frequency_bar_plotter(lengths)
    print("Files saved in '{}/'".format(dir_name))
    
def detect_from_file(filename):
    '''
    Calls CrossbillDetector to detect crossbill calls of a desired type. 
    Makes a new directory, then saves these detections using detections_to_files
    '''
    # read sample file within directory
    (samples, sample_rate) = read_wave_file(filename)
    
    # this function will be notified
    listener = _Listener()
    
    # get a single channel
    sample = channel_counter(samples, filename)
    
    # run detection pipeline
    type = 2
    detector = CrossbillDetector(sample_rate, listener, type)
    detector.detect(sample)
    detector.complete_detection()

    # find average length of clips
    #average_length(listener.clips, sample_rate)
    
    # make a "detections/" folder or similar if it doesn't already exist
    dir_name = make_dir("detections", 2)
    
    # create files in new folder and return lengths of files in samples
    lengths = detections_to_files(samples, listener.clips, sample_rate, dir_name)
    
    #  some final information
    #frequency_bar_plotter(lengths)
    print("Files saved in '{}/'".format(dir_name))


def main():
    # get file or folder as user input 
    input = input_validation() # function from parser.py
   
    if input['verbose']:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
    
    # if a file was provided, detect calls within it
    if input['file']:
        detect_from_file(input['file'])
        # TEST:
        #settings_testing(input['file'])
        return
    
    # if a directory was provided, detect calls within all files in directory
    elif input['dir']:
        directory = input['dir']
        
        # run detector on every file ending with .wav in directory
        for filename in listdir(directory):
            file_path = directory + filename
            if is_wav_file(file_path): # function from parser.py
                detect_from_file(file_path)
            else:
                logging.warning("Skipping '{}': not a .wav file".format(file_path))
    
    else:
        print("Please specify a file with -f or a directory with -d. For help use flag -h")   

main()