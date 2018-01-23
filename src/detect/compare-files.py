#compare-files.py
#Find if any samples are different from each other  
from glob import glob

# Return list of directories matching pattern detections-settings*
folder_list = glob('detections-settings*/')

# Create list of lists of .wav files in each folder
list_of_file_lists = []
for folder in folder_list:
    path = '{}/*.wav'.format(folder)
    file_list = glob(path)
    list_of_file_lists.append(file_list)
    
unique_files_lol = []
for file_list in list_of_file_lists:
    for file in file_list:
        for file_list_two in list_of_file_lists:
            if file not in file_list_two:
                print("{} is cool.".format(file))
        
    #add space in all the others if it's not in there