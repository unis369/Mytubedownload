# standard library imports
import argparse
import os
import platform
import subprocess

# third party imports
import cursor

# local library imports
from pytube import YouTube

video_audio = 'video codec'
resolution = ''
abr = ''
fps = 0
args = {}
fileobj = {}
download_count = 1
def main():
    global args
    global video_audio
    parser = argparse.ArgumentParser()

    parser.add_argument('url', help='指定YouTube視訊網址')
    
    parser.add_argument('-sd', action='store_true', help='選擇普通(480P)畫質')
    parser.add_argument('-hd', action='store_true', help='選擇HD(720P)畫質')
    parser.add_argument('-fhd', action='store_true', help='選擇Full HD(1080P)畫質')
    parser.add_argument('-a', action='store_true', help='僅下載聲音')
    args = parser.parse_args()
    video_audio = 'video codec'
    download_media(args)    # 下載video。


def download_media(args):
    global video_audio, resolution, abr, fps
    print()
    try:
        yt = YouTube(args.url,
                     on_progress_callback=onProgress,
                     on_complete_callback=onComplete
                     )
    except:
        print('下載影片時發生錯誤，請確認網路連線和YouTube網址無誤。')
        return

    filter = yt.streams.filter
    resolution_str = ''
    if args.a:   # 只下載聲音
        target = filter(type='audio').first()
    elif args.fhd:
        resolution_str = 'Full HD(1080P)'
        target = filter(type='video', resolution='1080p').first()
    elif args.hd:
        resolution_str = 'HD(720P)'
        target = filter(type='video', resolution='720p').first()
    elif args.sd:
        resolution_str = 'SD(480P)'
        target = filter(type='video', resolution='480p').first()
    else:
        # target = filter(type='video').first()
        resolutions = ('1080p', '720p', '480p', '360p', '240p')
        for r in resolutions:
            target = filter(type='video', resolution=r).first()
            if target is not None:
                break
        if target is None:
            target = filter(type='video').first()

    # print(target)
    # exit(0)

    if target is None:
        # print()
        print(f'沒有您指定的{resolution_str}解析度，可用的解析度如下：')
        res_list = video_res(yt)

        for i, res in enumerate(res_list):
            # print('{}) {}'.format(i + 1, res))
            print(f'   {i+1}) {res}')

        print()
        # val = input('請選擇(預設{})：'.format(res_list[0]))
        val = input(f'請選擇代碼(預設1)：')

        try:
            res = res_list[int(val)-1]
        except:
            res = res_list[0]

        # print()
        # print('您選擇的是 {} 。'.format(res))
        print(f'您選擇的解析度是 {res}。')
        target = filter(type='video', resolution=res).first()
        print()

    # print(type(target))
    # print(target)
    # print(target.resolution)
    # print(type(target.resolution))
    # exit(0)
    if args.a:
        abr = target.abr
        # bitrate = target.bitrate
        # print('bitrate:', bitrate)
        video_audio += '(' + abr + ')'
    else:
        resolution = target.resolution
        fps = target.fps
        video_audio += '(' + resolution + ')'

    # targets = vars(target)
    # for t in targets:
    #     print(t)
    cursor.hide()
    # 開始下載
    target.download(output_path=pyTube_folder())
    cursor.show()


# 檔案下載的回呼函式
def onProgress(stream, chunk, remains):
    global video_audio
    total = stream.filesize
    percent = (total-remains) / total * 100
    # print('下載中… {:05.2f}%'.format(percent), end='\r')
    print(f'下載{video_audio}中...{percent:6.2f}%', end='\r')


# 檔案下載的回呼函式
def onComplete(stream, file_name):
    global download_count, fileobj, video_audio
    fileobj['name'] = os.path.basename(file_name)
    fileobj['dir'] = os.path.dirname(file_name)
    # print('\r')
    print(file_name)

    if download_count == 1:
        if check_media(file_name) == -1:
            # print('此影片沒有聲音。')
            download_count += 1
            try:
                # 視訊檔重新命名
                os.rename(file_name, os.path.join(
                    fileobj['dir'], 'temp_video.mp4'))
            except:
                print('視訊檔重新命名失敗。')
                return

            # print('準備下載聲音檔...')
            vars(args)['a'] = True    # 設定成a參數，表示只下載audio codec。
            video_audio = 'audio codec'
            # print()
            # cursor.hide()
            download_media(args)   # 下載audio。
            # cursor.show()
        else:
            print('此影片有聲音，下載完畢。')
    else:
        try:
            # 聲音檔重新命名
            os.rename(file_name, os.path.join(
                fileobj['dir'], 'temp_audio.mp4'))
        except:
            print('聲音檔重新命名失敗。')

        # 合併video/audio
        merge_media(file_name)


# 檢查影片檔是否包含聲音
def check_media(file_name):
    '''本函數呼叫的外部程式ffprobe偶爾會誤判，下載的codec中明明沒有audio，卻傳回非-1的值，
    表示「有聲音」，所以主程式便不再下載audio codec。

    由於ffprobe是外部程式，無法追蹤，乾脆改為不用ffprobe判斷，固定傳回-1，表示沒有聲音，
    原download的codec不管有無audio，主程式一律再下載audio然後合併。這樣可保證有影有聲。

    經測試，即使原來的codec有audio，再下載audio合併，也不會影響音效，頂多是花多點時間而已。

    而且高解析度的video很少會有audio的，所以影響效能的機會很低。
    '''

    return -1

    # r = subprocess.Popen(['ffprobe', file_name],
    #                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # out, err = r.communicate()

    # if (out.decode('utf-8').find('Audio') == -1):
    #     return -1  # 沒有聲音
    # else:
    #     return 1


# 合併video/audio
def merge_media(file_name):
    global resolution, abr, fps

    print('video codec和audio codec合併中...')
    print()
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
        print()
        print()
        print('video codec和audio codec合併完成。存放路徑和檔名：')
        print(file_name)
        spaces = ' ' * 7
        print(f'\tresolution: {resolution} / fps: {fps}{spaces}abr: {abr}')
        print()
    except:
        print()
        print('video codec和audio codec合併失敗。')
    finally:
        print()


def pyTube_folder():
    #     sys = platform.system()
    #     home = os.path.expanduser('~')
    #
    #     # print(sys)
    #     # exit()
    #     if sys == 'Windows':
    #         folder = os.path.join(home, 'Videos', 'PyTube')
    #     elif sys == 'Linux':
    #         folder = os.path.join(home, 'Movies', 'PyTube')
    #         print(type(folder))
    #         exit(0)
    #     elif sys == 'Darwin':
    #         folder = os.path.join(home, 'Movies', 'PyTube')

    #     if not os.path.isdir(folder):  # 若'PyTube'資料夾不存在…
    #         os.mkdir(folder)        # 則新增資料夾

    #     return folder
    return os.getcwd()


def video_res(yt):
    res_set = set()
    # video_list = yt.streams.filter(type='video').all()
    video_list = yt.streams.filter(type='video')
    for v in video_list:
        res_set.add(v.resolution)

    return sorted(res_set, reverse=True, key=lambda s: int(s[:-1]))


if __name__ == '__main__':
    main()