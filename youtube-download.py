from pytube import YouTube

YouTube('https://www.youtube.com/watch?v=Qmla9NLFBvU').streams.first().download()
    