import pytube
video_url = 'https://youtu.be/N_s4G-QrhfQ' 
# copy and paste url
youtube = pytube.YouTube(video_url)
video = youtube.streams.first()
video.download('c:\temp\') # path, where to video download.
# it may take some tome to download.