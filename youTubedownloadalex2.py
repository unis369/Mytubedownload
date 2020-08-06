# from pytube import YouTube
import pytube

with open('./list.txt', 'r') as f_stream:
    count = 1
    line = f_stream.readline()
    while line:
        print(count, line)
        yt = pytube.YouTube(line)
        yt.streams.first().download(filename='test' + str(count))
        count += 1
        line = f_stream.readline()