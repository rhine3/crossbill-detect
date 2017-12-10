from old_bird_detector_redux_1_1 import ThrushDetector, TseepDetector
from audio_file_utils import read_wave_file, write_wave_file
from bunch import Bunch
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
	- detections: a list of tuples of detection start time and length in samples 
	  created by _Listener's method, process_clip
	- sample_rate: integer sample rate
	'''
	
	for detection in detections:
		(start, length) = detection
		path = "detections/clip{}.wav".format(start)
		clip = samples[0][start:start+length]
		write_wave_file(path, clip, sample_rate)
		print("{} saved".format(clip))
		
def main():		
	# read sample file within directory
	(samples, sample_rate) = read_wave_file("sample.wav")
	print(samples)
	
	# only feed one channel into ThrushDetector
	if len(samples) > 1:
		sample = samples[0]
	else:
		sample = samples
	
	listener = _Listener()
	
	detector = ThrushDetector(sample_rate, listener)
	detector.detect(sample)
	detector.complete_detection()

	detections_to_files(samples, listener.clips, sample_rate)

main()