from old_bird_detector_redux_1_1 import CrossbillDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch
from os import path, makedirs
import numpy

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
		
		# skip detection if long detection--I have no idea why all the detections are 4205 samples long
		if length != 4205:
			print(length)
			continue
		
		# create filename indicating clip start in milliseconds
		start_sec = int(1000 * start/sample_rate)
		filename = "detections/clip{}.wav".format(start_sec)
		
		# create 2D numpy array of detections
		clip = numpy.array([samples[0][start:start+length], samples[1][start:start+length]], numpy.int32)
		
		# warning: will overwrite any clips that already exist
		write_wave_file(filename, clip, sample_rate)
		print("{} saved".format(filename))
		
def main():
	# read sample file within directory
	# PUT FILENAME HERE
	(samples, sample_rate) = read_wave_file("sample.wav")
	
	listener = _Listener()
	
	# if samples is 2D, only feed first subarray into ThrushDetector
	if len(samples) > 1:
		assert samples[0].all() == samples[1].all()
		sample = samples[0]
	else:
		sample = samples
	
	detector = CrossbillDetector(sample_rate, listener)
	detector.detect(sample)
	detector.complete_detection()

	#average_length(listener.clips, sample_rate)
	
	detections_to_files(samples, listener.clips, sample_rate)

main()