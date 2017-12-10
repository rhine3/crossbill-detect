from old_bird_detector_redux_1_1 import ThrushDetector, TseepDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch
from os import path, makedirs
import numpy

class _Listener:
    
    def __init__(self):
        self.clips = []
        
    def process_clip(self, start_index, length):
        self.clips.append((start_index, length))

def detections_to_files(samples, detections, sample_rate):
	'''
	Uses write_wave_file() from Vesper's audio_file_utils to write audio files given 
	their start time and length in samples.
	
	- samples: a single-channel numpy array of samples
	- detections: a list of tuples (detection_start_time, detection_length) 
	  created by _Listener's method, process_clip
	- sample_rate: integer sample rate
	'''
	
	# make a "detections/" folder if it doesn't already exist
	if not path.exists('detections'):
		makedirs('detections')
	
	# write clips to "detections/"
	for detection in detections:
		(start, length) = detection
		
		filename = "detections/clip{}.wav".format(start)
		
		clip = samples[0][start:start+length]
		
		# warning: will overwrite any clips that already exist
		write_wave_file(filename, clip, sample_rate)
		print("{} saved".format(clip))
		
def main():
	# read sample file within directory
	(samples, sample_rate) = read_wave_file("sample.wav")
	print(samples)
	
	listener = _Listener()
	
	# if samples is 2D, only feed first subarray into ThrushDetector
	if len(samples) > 1:
		assert samples[0].all() == samples[1].all()
		sample = samples[0]
	else:
		sample = samples
	
	detector = ThrushDetector(sample_rate, listener)
	detector.detect(sample)
	detector.complete_detection()

	
	detections_to_files(samples, listener.clips, sample_rate)

main()