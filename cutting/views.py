import os

from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import render
from django.utils.encoding import escape_uri_path
import json
from .config import DOWNLOAD_DIR
from .utils import cut


def getPage(request):
    return render(request, 'formPage.html')


def cutVideo(request):
    """
    根据前端发来的视频链接及切分点进行切分
    问题是下载视频可能会耗费很长时间，导致交互失败
    :param request:
    :return:
    """
    post_body = request.body
    json_result = json.loads(post_body)
    file_name = json_result['file_name']
    video_time_seg = json_result['video_time_seg']
    audio_time_seg = json_result['audio_time_seg']
    video_time_seg = video_time_seg.split(',')
    audio_time_seg = audio_time_seg.split(',')
    file_abs_path = os.path.join(DOWNLOAD_DIR, file_name)
    file_prefix = file_name.split(".")[0]
    video_seg_name, audio_seg_name = cut(file_abs_path, video_time_seg, audio_time_seg, file_prefix)
    # print(video_seg_name)
    # print(audio_seg_name)
    result = {'video_seg_name': video_seg_name, 'audio_seg_name': audio_seg_name}
    return HttpResponse(json.dumps(result), content_type="application/json")


def downloadFile(request):
    """
    前端传文件名，返回一个文件供前端下载
    :param request:
    :return:
    """
    file_name = request.GET.get('fileName')
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
    temp = 'attachment;filename*=utf-8{}'.format(escape_uri_path(file_name))
    response['Content-Disposition'] = temp
    return response


def uploadFile(request):
    """
    上传文件
    :param request:
    :return:
    """
    if request.method == "POST":
        file = request.FILES.get('file', None)
        if not file:
            return HttpResponse("no files for upload!")
        if not os.path.exists(DOWNLOAD_DIR):
            os.mkdir(DOWNLOAD_DIR)
        destination = open(os.path.join(DOWNLOAD_DIR, file.name), 'wb+')
        print("upload file {}".format(file.name))
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        return HttpResponse("upload over!")
