import os
import subprocess

import pytube

yt = pytube.YouTube("https://www.youtube.com/watch?v=kFzViYkZAz4")

vids= yt.streams.all()
for i in range(len(vids)):
    print(i,'. ',vids[i])

vnum = int(input("Enter vid num: "))

parent_dir = r"C:\temp"
vids[vnum].download(parent_dir)

new_filename = input("Enter filename (including extension): ")
# e.g. new_filename.mp3

default_filename = vids[vnum].default_filename  
# get default name using pytube API
subprocess.call(['ffmpeg', '-i',                
# or subprocess.run (Python 3.5+)
    os.path.join(parent_dir, default_filename),
    os.path.join(parent_dir, new_filename)
])

print('done')