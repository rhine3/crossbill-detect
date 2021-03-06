'''
crossbill_detector.py
by Tessa Rhinehart

Wrapper for Harold Mill's reimplementation of the Old Bird NFC detectors.

Usage: 
$ python crossbill_detector.py -f <filename.wav>
$ python crossbill_detector.py -d <directory-of-wav-files/>
'''

# Harold Mills's utilities (my modifications: CrossbillDetector & OpenDetector)
from old_bird_detector_redux_1_1 import CrossbillDetector, OpenDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch 

# Various ops related to reading in samples and saving detections
from os import makedirs, listdir
from shutil import rmtree
import numpy # write_wave_file takes detections in the form of an nparray
from ntpath import basename # for finding filename within path

# Own utility to plot bar chart of lengths of detections in sample
from plotter import frequency_bar_plotter

# For validating files/directories and using command line arguments
from argument_parser import is_directory, is_wav_file, input_validation

# For levels of verbosity in error logging
import logging

repo_path = 'C:/Users/tessa/drive/red-crossbills/crossbill-detect'

### Class for direct interaction with detector objects
class _Listener:
    '''A listener that interacts with the Old Bird Detector Redux (OBDR).
    Methods include:
        - extract_single_channel(): put samples in correct format for the OBDR
        - append_detection(): called for every detection found by the OBDR
        - detections_to_files(): save all detections as .wav files
        - average_length: calculate average length of detections
    '''
    
    def __init__(self, source_file, samples, sample_rate):
        self.sample_rate = sample_rate
        self.samples = self.extract_single_channel(source_file, samples)
        self.detections = [] #to be filled in by append_detections()
      
      
    def append_detection(self, start_index, length):
        '''Called for every clip found by Old Bird detector'''
        self.detections.append((start_index, length))
     
     
    def extract_single_channel(self, source_path, samples):
        '''
        Returns the first subarray from `samples`, a two-dimensional array of 
        channels of sound read from a .wav file. The array returned is in the 
        format required by the OBDR.
        '''
        
        filename = basename(source_path)
        
        if len(samples) > 1:
            if len(samples) == 2: 
                if samples[0].all() == samples[1].all():
                    warn_str = "File '{}' contains two identical channels as read".format(filename)
              
                else:
                    warn_str = "File '{}' contains two non-identical channels as read".format(filename)
            else:
                warn_str = "Multiple channels in file '{}' as read".format(filename)
            
            logging.warning(warn_str)
            logging.info("Processing first channel")
            return samples[0]
            
        elif len(samples) == 1:
            logging.info("Processing single channel in file '{}'".format(filename))
            return samples[0]
            
        else:
            logging.info("File {} is empty".format(filename))
            return []
    

    def detections_to_files(self, dir_name, recording_name):
        '''
        Uses write_wave_file() from Vesper's audio_file_utils to write a mono
        audio file given their start time and length in samples.
        '''
        
        lengths = []
        logging.info("Saving files from {}.wav".format(recording_name))
        
        # write detections to `dir_name/`
        for detection in self.detections:
            (start, length) = detection
            
            lengths.append(length)
            
            # issue: why are so many of the correct detections 4205 samples long
            #if length != 4205:
            #   logging.info(length)
            #   continue
            
            # create filename indicating detection origin and start in ms
            start_sec = int(1000 * start/self.sample_rate)
            filename = "{}/{}_{}ms.wav".format(dir_name, 
                       recording_name, start_sec)
            
            # create numpy array of detections (mono file)
            clip = numpy.array([self.samples[start:start+length], self.samples[start:start+length]], numpy.int32)
            
            # warning: will overwrite any clips that already exist
            write_wave_file(filename, clip, self.sample_rate)
            logging.info("{} saved".format(filename))
            
        return lengths
     
    
    def average_length(self):
        '''
        Compute average length in number of samples--only non-outliers (<0.05)
        '''
        
        num_detections = 0
        sample_total = 0
        
        # calculate upper limit of number of samples--higher than 0.15 sec implies detection outlier
        upper_limit = 0.15 * self.sample_rate
        #logging.info(upper_limit)
        
        for detection in self.detections:
            detection_length = detection[1]
            if detection_length < upper_limit:
                logging.info("Detection exceeds determined sample limit \
                             ({} samples)".format(detection_length))
                num_detections += 1
                sample_total += detection_length
        
        avg_samples = sample_total / num_detections
        logging.info(avg_samples)
        logging.info(avg_samples*sample_rate)
    
    
### Miscellaneous and wrapper functions

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

def detect_from_file(file_path, settings = None):
    '''
    
    Creates a detector object to detect crossbill calls of a desired type. 
    Makes a new directory, then saves these detections using detections_to_files
    
    If settings are provided, creates an "OpenDetector" which allows
    the user to call the detector with their own settings. Otherwise, creates CrossbillDetector.
    '''
    
    # Generate a two-dimensional numpy array frome wave file
    # nparray is of shape (num_channels, num_samples)
    (samples, sample_rate) = read_wave_file(file_path)
    
    # This function will be notified by the detector
    listener = _Listener(file_path, samples, sample_rate)
    
    # Run detection pipeline
    if settings:
        detector = OpenDetector(sample_rate, listener, settings)
    else:
        type = 2
        detector = CrossbillDetector(sample_rate, listener, type)
        
    detector.detect(listener.samples)
    detector.complete_detection()

    # Find average length of clips
    #average_length(listener.clips, sample_rate)
    
    # Make a "detections/" dir or similar if it doesn't already exist
    if settings: preferred_name = repo_path+"/detections-"+settings.name
    else: preferred_name = repo_path+"/detections"
    # Option 2: add number to directory name if preferred dir already exists
    dir_name = make_dir(preferred_name, 2) 
    
    # Create files in new directory and return lengths of files in samples
    recording_name = basename(file_path).replace('.wav','')
    lengths = listener.detections_to_files(dir_name, recording_name)
    
    #  Print final information
    #frequency_bar_plotter(lengths)
    print("Files saved in '{}/'".format(dir_name))


def main():
    # Get file or folder as user input 
    input = input_validation() # function from parser.py
   
    if input['verbose']:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
    
    # If user provided a file, detect calls within it
    if input['file']:
        detect_from_file(input['file'])
        return
    
    # If user provided a directory, detect calls within all files in directory
    elif input['dir']:
        directory = input['dir']
        
        # Run detector on every file ending with .wav in directory
        for filename in listdir(directory):
        
            file_path = directory + filename
            if is_wav_file(file_path): # function from parser.py
                detect_from_file(file_path)
            else:
                logging.warning("Skipping '{}': not a .wav file".format(file_path))
    
    else:
        print("Please specify a file with -f or a directory with -d. For help use flag -h")   

main()
