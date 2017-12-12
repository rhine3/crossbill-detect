
import matplotlib.pyplot as plt

def frequency_bar_plotter(array):
    '''
    Creates a bar plot of an array, with unique array elements as
    x-axis and the frequency of each element within the array 
    as the y-axis. (Doesn't actually plot yet!)
    '''
    dict = {}
    
    
    for element in array:
        if element not in dict:
            dict[element] = 1
        else:
            dict[element] += 1
    
    buckets = []
    vals = []
    
    for key, value in dict.items():
        buckets.append(key)
        vals.append(value)
        print("{} samples: {} clips.".format(key, value))
    
