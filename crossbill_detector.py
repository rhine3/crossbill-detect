# Harold Mills's utilities (CrossbillDetector is my modification to the original ThrushDetector)
from old_bird_detector_redux_1_1 import CrossbillDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch 

# Various ops related to reading in samples and saving detections
from os import path, makedirs, listdir
from shutil import rmtree
import numpy # write_wave_file takes detections in the form of an nparray

# Own utility to plot bar chart of lengths of detections in sample
from plotter import frequency_bar_plotter

# For validating and using command-line arguments
import argparse

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
    If directory does exist:
        - if mode is 0, function doesn't delete previous directory or make a new directory
        - if mode is 1, function recursively deletes everything in preexisting directory
        - if mode is 2, function makes a new directory with a number appended to it
    '''
    
    if not path.exists(dir_name):
        print("Making directory '{}/'.".format(dir_name))
        makedirs(dir_name)
    elif mode == 0:
        print("Warning: '{}/' already exists. Some contents may be overwritten.".format(dir_name))
    elif mode == 1:
        print("Deleting previous directory")
        rmtree(dir_name)
    else: #mode == 2
        increment = 2
        new_name = dir_name + str(increment)
        while path.exists(new_name):
            increment += 1
            new_name = dir_name + str(increment)
        dir_name = new_name
        print("Making directory '{}/'.".format(dir_name))
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
    
def detect_from_file(filename):
    # read sample file within directory
    (samples, sample_rate) = read_wave_file(filename)
    type = 2
    
    # this function will be notified
    listener = _Listener()
    
    # get a single channel
    sample = channel_counter(samples, filename)
    
    # run detection pipeline
    detector = CrossbillDetector(sample_rate, listener, type)
    detector.detect(sample)
    detector.complete_detection()

    # find average length of clips
    #average_length(listener.clips, sample_rate)
    
    # make a "detections/" folder or similar if it doesn't already exist
    dir_name = make_dir("detections", 2)
    
    # create files in new folder and return lengths of files in samples
    lengths = detections_to_files(samples, listener.clips, sample_rate, dir_name)
    
    # plot lengths of detections
    frequency_bar_plotter(lengths)
    
    # print confirmation
    print("Files saved in '{}/'".format(dir_name))
   
def is_wav_file(filename):
    '''Returns True if filename is an existing .wav file, False otherwise'''
    if path.isfile(filename) and filename.endswith('.wav'):
        return True
    return False
    
def parse_file(filename):
    '''For parsing arguments with flag -f or --file'''
    if not is_wav_file(filename):
        msg = "'{}' is not a valid .wav file.".format(filename)
    return filename

def parse_directory(dir):
    '''For parsing arguments with flag -d or --dir'''
    if not path.exists(dir): 
        msg = "'{}/' is not a valid directory.".format(dir)
        raise argparse.ArgumentTypeError(msg)
    return dir
    

def input_validation():
    '''
    Will eventually be used to get user input from command line arg--either a file or a folder
    '''
    # initialize ArgumentParser
    parser = argparse.ArgumentParser(
        description='Detect crossbill calls from 16-bit wav files. \
            Can be run with a single .wav file or with a folder of .wav files.', add_help=True)
    
    # add argument options for a single file or a directory
    files = parser.add_mutually_exclusive_group(required=False)
    files.add_argument('-f', '--file', metavar='FILE.wav', type=parse_directory, action='store', dest='file',
        help='detect calls in a .wav file')
    
    # add argument for which type is in the file (currently nothing is done with this information)
    files.add_argument('-d', '--dir', metavar='DIRECTORY/', type=parse_file, action='store', dest='dir',
        help='detect calls in all .wav files within directory')
        
    parser.add_argument('-t', '--type', metavar='TYPE', type=int, action='store', dest='type', 
        help='a crossbill call type from 1 to 10')
    args = parser.parse_args()
    return vars(args)
    

def main():
    # get file or folder as user input
    input = input_validation()
    
    # if a file was provided, detect calls within it
    if input['file']:
        print("Detecting .")
        detect_from_file(input.file)
        return
    
    # if a directory was provided, detect calls within all files in directory
    elif input['dir']:
        print("Got a directory.")
        directory = input['dir']
        
        # run detector on every file ending with .wav in directory
        for filename in listdir(directory):
            file_path = directory + '/' + filename
            print(file_path)
            if is_wav_file(file_path):
                detect_from_file(file_path)
    
    else:
        print("Please specify a file with -f or a directory with -d. For help use flag -h.")   

main()