import os
import platform
from pytube import YouTube
import subprocess
 
args = {}
fileobj = {}
download_count = 1
 
 
def pyTube_folder():
    sys = platform.system()
    home = os.path.expanduser('~')
 
    if sys == 'Windows':
        folder = os.path.join(home, 'Videos', 'PyTube')
    elif sys == 'Darwin':
        folder = os.path.join(home, 'Movies', 'PyTube')
 
    if not os.path.isdir(folder):  # 若'PyTube'資料夾不存在…
        os.mkdir(folder)        # 則新增資料夾
 
    return folder
 
 
def onProgress(stream, chunk, file_handle, remains):
    total = stream.filesize
    percent = (total-remains) / total * 100
    print('下載中… {:05.2f}%'.format(percent), end='\r')
 
 
def video_res(yt):
    res_set = set()
    video_list = yt.streams.filter(type="video").all()
    for v in video_list:
        res_set.add(v.resolution)
 
    return sorted(res_set, reverse=True, key=lambda s: int(s[:-1]))
 
 
def download_media(args):
    try:
        yt = YouTube(args.url, on_progress_callback=onProgress,
                     on_complete_callback=onComplete)
    except:
        print('下載影片時發生錯誤，請確認網路連線和YouTube網址無誤。')
        return
 
    filter = yt.streams.filter
 
    if args.a:  # 只下載聲音
        target = filter(type="audio").first()
    elif args.fhd:
        target = filter(type="video", resolution="1080p").first()
    elif args.hd:
        target = filter(type="video", resolution="720p").first()
    elif args.sd:
        target = filter(type="video", resolution="480p").first()
    else:
        target = filter(type="video").first()
 
    if target is None:
        print('沒有您指定的解析度，可用的解析度如下：')
        res_list = video_res(yt)
 
        for i, res in enumerate(res_list):
            print('{}) {}'.format(i+1, res))
 
        val = input('請選擇（預設{}）：'.format(res_list[0]))
 
        try:
            res = res_list[int(val)-1]
        except:
            res = res_list[0]
 
        print('您選擇的是 {} 。'.format(res))
        target = filter(type="video", resolution=res).first()
 
    # 開始下載
    target.download(output_path=pyTube_folder())
 
 
# 檢查影片檔是否包含聲音
def check_media(filename):
    r = subprocess.Popen(["ffprobe", filename],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = r.communicate()
 
    if (out.decode('utf-8').find('Audio') == -1):
        return -1  # 沒有聲音
    else:
        return 1
 
# 合併影片檔
def merge_media():
    temp_video = os.path.join(fileobj['dir'], 'temp_video.mp4')
    temp_audio = os.path.join(fileobj['dir'], 'temp_audio.mp4')
    temp_output = os.path.join(fileobj['dir'], 'output.mp4')
 
    cmd = f'ffmpeg -i {temp_video} -i {temp_audio} \
        -map 0:v -map 1:a -c copy -y {temp_output}'
    try:
        subprocess.call(cmd, shell=True)
        # 視訊檔重新命名
        os.rename(temp_output, os.path.join(fileobj['dir'], fileobj['name']))
        os.remove(temp_audio)
        os.remove(temp_video)
        print('視訊和聲音合併完成')
    except:
        print('視訊和聲音合併失敗')
 
# 檔案下載的回呼函式
def onComplete(stream, file_handle):
    global download_count, fileobj
    fileobj['name'] = os.path.basename(file_handle.name)
    fileobj['dir'] = os.path.dirname(file_handle.name)
    print('\r')
 
    if download_count == 1:
        if check_media(file_handle.name) == -1:
            print('此影片沒有聲音')
            download_count += 1
            try:
                # 視訊檔重新命名
                os.rename(file_handle.name, os.path.join(
                    fileobj['dir'], 'temp_video.mp4'))
            except:
                print('視訊檔重新命名失敗')
                return
 
            print('準備下載聲音檔')
            vars(args)['a'] = True  # 設定成a參數
            download_media(args)    # 下載聲音
        else:
            print('此影片有聲音，下載完畢！')
    else:
        try:
            # 聲音檔重新命名
            os.rename(file_handle.name, os.path.join(
                fileobj['dir'], 'temp_audio.mp4'))
        except:
            print("聲音檔重新命名失敗")
        # 合併聲音檔
        merge_media()
 
 
def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="指定YouTube視訊網址")
    parser.add_argument("-sd", action="store_true", help="選擇普通（480P）畫質")
    parser.add_argument("-hd", action="store_true", help="選擇HD（720P）畫質")
    parser.add_argument("-fhd", action="store_true", help="選擇Full HD（1080P）畫質")
    parser.add_argument("-a", action="store_true", help="僅下載聲音")
 
    args = parser.parse_args()
    download_media(args)
 
 
if __name__ == '__main__':
    main()