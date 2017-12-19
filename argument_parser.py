'''For validating and using command-line arguments.'''
from os import path
import argparse

def is_directory(pathname):
    '''Returns True if pathname is an existing directory, False otherwise'''
    if path.exists(pathname):
        return True
    return False

def is_wav_file(filename):
    '''Returns True if filename is an existing .wav file, False otherwise'''
    if path.isfile(filename) and filename.endswith('.wav'):
        return True
    return False
    
def _parse_file(filename):
    '''For parsing arguments with flag -f or --file'''
    if not is_wav_file(filename):
        msg = "'{}' is not a valid .wav file.".format(filename)
    return filename

def _parse_directory(dir):
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
    files.add_argument('-f', '--file', metavar='FILE.wav', type=_parse_directory, action='store', dest='file',
        help='detect calls in a .wav file')
    
    # add argument for which type is in the file (currently nothing is done with this information)
    files.add_argument('-d', '--dir', metavar='DIRECTORY/', type=_parse_file, action='store', dest='dir',
        help='detect calls in all .wav files within directory')
        
    parser.add_argument('-t', '--type', metavar='TYPE', type=int, action='store', dest='type', 
        help='a crossbill call type from 1 to 10')
    args = parser.parse_args()
    return vars(args)
    