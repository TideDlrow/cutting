import os
import time
from . import config
import requests


def cut(file_path, video_time_seg, audio_time_seg, file_prefix=None):
    """
    :param file_prefix: 切分后的文件前缀，默认为当前时间戳
    :param file_path: 视频文件路径，最好是绝对路径
    :param video_time_seg: 视频时间段 数组(长度必须是偶数) 可以用end来代表视频的末尾
    :param audio_time_seg: 音频时间段 数组(长度必须是偶数) 可以用end来代表视频的末尾
    :return: 视频和音频片段文件名数组组成的元组
    """
    print(audio_time_seg)
    if file_prefix is None:
        file_prefix = int(time.time())
    cmd_end_time = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 " \
                   "-sexagesimal {}".format(
        file_path)
    # 视频总长度
    video_end_time = os.popen(cmd_end_time).read().strip()
    # 切分后的文件名
    video_seg_name = []
    if len(video_time_seg) >= 2:
        for i in range(0, len(video_time_seg), 2):
            begin_time = video_time_seg[i]
            end_time = video_time_seg[i + 1]
            if begin_time.lower() == config.END_TIME_ALIAS:
                begin_time = video_end_time
            if end_time.lower() == config.END_TIME_ALIAS:
                end_time = video_end_time
            # 每个片段的文件名
            seg_name = "{}-{}-video.mp4".format(file_prefix, int(i / 2))
            load_path = os.path.join(config.UPLOAD_DIR, seg_name)
            cmd = "ffmpeg -y -i {} -ss {} -to {}  -c copy -copyts {} -loglevel quiet".format(file_path, begin_time,
                                                                                             end_time,
                                                                                             load_path)
            os.system(cmd)
            video_seg_name.append(seg_name)

    # print("Video cutting finished")
    audio_seg_name = []
    if len(audio_time_seg) >= 2:
        for i in range(0, len(audio_time_seg), 2):
            begin_time = audio_time_seg[i]
            end_time = audio_time_seg[i + 1]
            if begin_time.lower() == config.END_TIME_ALIAS:
                begin_time = video_end_time
            if end_time.lower() == config.END_TIME_ALIAS:
                end_time = video_end_time
            seg_name = "{}-{}-audio.mp4".format(file_prefix, int(i / 2))
            load_path = os.path.join(config.UPLOAD_DIR, seg_name)
            cmd = "ffmpeg -y -i {} -ss {} -to {}  -acodec copy -vn {} -loglevel quiet".format(file_path, begin_time,
                                                                                              end_time,
                                                                                              load_path)
            os.system(cmd)
            audio_seg_name.append(seg_name)
    return video_seg_name, audio_seg_name


def download(link, file_name=None, download_dir=config.UPLOAD_DIR):
    """

    :param {str} link: 下载链接
    :param file_name: 下载后的文件名，默认以链接中以/分割后最后一个元素命名。如果链接中不存在/则会以链接命名
    :param download_dir: 下载后文件的存放目录
    :return: 文件的绝对路径
    """
    # 下载文件
    file = requests.get(link)
    # 若文件夹不存在 则创建
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    if file_name is None:
        file_name = link.split('/')[-1]
    # 下载后存放文件的路径
    file_path = download_dir + '/' + file_name
    # 把下载的文件存到相应的文件中
    with open(file_path, "wb") as code:
        code.write(file.content)
    return file_path


def remove_previous_files(dir, time):
    """
    删除给定目录下，创建时间在time之前的文件
    :param dir: 指定的目录
    :param time: 时间戳，单位为秒
    :return:
    """
    file_names = os.listdir(dir)
    file_list = [os.path.join(dir, file_name) for file_name in file_names]
    for file in file_list:
        # 判断是否为文件，如果不是文件则不进行操作
        if os.path.isfile(file):
            # 获取文件的创建时间
            file_create_time = os.path.getctime(file)
            # 若文件创建时间小于给定的时间，则删除
            if file_create_time < time:
                os.remove(file)
