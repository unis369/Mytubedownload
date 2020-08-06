import pytube 
yt = pytube.YouTube("https://www.youtube.com/watch?v=kFzViYkZAz4")

vids= yt.streams.all()
for i in range(len(vids)):
    print(i,'. ',vids[i])

vnum = int(input("Enter vid num: "))
vids[vnum].download(r"C:\temp")
print('done')
