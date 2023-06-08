from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, HttpResponse
from django.contrib import messages
from django.db import connection
# from pytube import YouTube
import io 
import os
import yt_dlp
import urllib
import datetime
import base64
from django.core.files.base import ContentFile

yt_video = None

# class Video:

class Video:
    
    def __init__(self,url):
        
        self.url = url
        
        self.videos = []
        self.audios = []
        with yt_dlp.YoutubeDL() as ydl:
            self.info = ydl.extract_info(self.url, download=False)
        for vid_format_details in self.info["formats"]:
            if vid_format_details["resolution"] == "audio only":
                aud = str(int(vid_format_details["abr"])) + " kbits/s"
                if all(aud not in list(auds.values()) for auds in self.audios):
                    self.audios.append({"quality": aud, "id": vid_format_details["format_id"]})
                    # audios.append({"quality": aud, "url": vid_format_details["url"]})
            elif vid_format_details["vcodec"] != "none" :
                if vid_format_details["acodec"] != "none" and vid_format_details["fps"] > 20:
                    vid = vid_format_details["format_note"] 
                    if all(vid not in list(vids.values()) for vids in self.videos):
                        # videos.append({"quality": vid, "url": vid_format_details["url"]})
                        self.videos.append({"quality": vid, "id": vid_format_details["format_id"]})
        
        
    # =================================== Getting Video Title ===========================================
    
    def vid_title(self):
        
        return self.info["title"]
    
    # =================================== Getting Video Length ===========================================
    
    def vid_duration(self):
        length = self.info["duration"]
        vid_length = str(datetime.timedelta(seconds=length))
        if vid_length.split(":")[0] == "00":
            return vid_length[3:]
        else:
            return vid_length
    # =================================== Getting Video Thumbnail =======================================
    
    def vid_thumbnail(self):
        
        self.thumbnail =  self.info["thumbnail"]
        # Requesting image from url
        self.raw_data = urllib.request.urlopen(f"{self.thumbnail}").read()
        self.image = io.BytesIO(self.raw_data)
    
        return base64.b64encode(self.image.getvalue()).decode('utf8')
    




# Create your views here.
def index(request):
    return render(request, 'index.html')

def get_vid_details(request):
    global yt_video
    yt_video = Video(request.POST.get('video_link'))
    thumbnail = yt_video.vid_thumbnail()
    duration = yt_video.vid_duration()
    title = yt_video.vid_title()
    # params = {"vid_resolutions": yt_video.res, "vid_thumbnail": thumbnail, "vid_duration": duration, 
    #                 "vid_title": title}
    params = { "vid_thumbnail": thumbnail, "vid_duration": duration, 
                    "vid_title": title, "vid_resoltuions": yt_video.videos, "audio_resolutions": yt_video.audios}
    return  render(request, "card_vid_detail.html", params)

# def download_vid(request):
#     global yt_video
#     if request.POST.get('vid_type') == "mp3":
#         with open(yt_video.url.streams.filter(only_audio=True).first().download(filename='file.mp3', skip_existing=True),'rb') as f:
#             data = base64.b64encode(f.read())
#         yt_vid_name = yt_video.url.streams.filter(only_audio=True).first().default_filename
#         if ".mp4" in yt_vid_name:
#             yt_vid_name = yt_vid_name.replace('.mp4', "")
        
#         return JsonResponse({"data": data.decode('utf8'), "filename": yt_vid_name, "mimetype": "audio/mp3"}) 

#     else:
#         with open(yt_video.url.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(filename='file.mp4', skip_existing=True),'rb') as f:
#             data = base64.b64encode(f.read())
#         yt_vid_name = yt_video.url.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().default_filename
#         if ".mp4" in yt_vid_name:
#             yt_vid_name = yt_vid_name.replace('.mp4', "")
#         return JsonResponse({"data": data.decode('utf8'), "filename": yt_vid_name, "mimetype": "video/mp4"}) 
        

def download_vid(request):
    global yt_video
    download_id = request.POST.get("tag")
    download_type = request.POST.get("download_type")
    download_mimetype = request.POST.get("mimetype")
    option_details = {}
    data = None
    if os.path.exists("file.mp4"):
        os.remove("file.mp4")
    if os.path.exists("file.mp3"):
        os.remove("file.mp3")
    
    if download_type == "mp4":
        option_details = {"format": download_id, 'outtmpl': './file.mp4'} 
        with yt_dlp.YoutubeDL(option_details) as ydl:
            ydl.download(yt_video.url)
        with open('file.mp4','rb') as f:
            data = base64.b64encode(f.read())
    if download_type == "mp3":
        option_details = {"format": download_id, 'outtmpl': './file.mp3'} 
        with yt_dlp.YoutubeDL(option_details) as ydl:
            ydl.download(yt_video.url)
        with open('file.mp3','rb') as f:
            data = base64.b64encode(f.read())
    yt_vid_name = yt_video.info["title"]
    return JsonResponse({"data": data.decode('utf8'), "filename": yt_vid_name, "mimetype": "audio/mp3"})
    
    
    
    
    
    
    with open(yt_video.url.streams.get_by_itag(download_id).download(filename=f'file.{download_type}', skip_existing=True),'rb') as f:
            data = base64.b64encode(f.read())
    yt_vid_name = yt_video.url.streams.filter(only_audio=True).first().default_filename
    if ".mp4" in yt_vid_name:
        yt_vid_name = yt_vid_name.replace('.mp4', "")
        
    return JsonResponse({"data": data.decode('utf8'), "filename": yt_vid_name, "mimetype": download_mimetype}) 

    # else:
    #     with open(yt_video.url.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(filename='file.mp4', skip_existing=True),'rb') as f:
    #         data = base64.b64encode(f.read())
    #     yt_vid_name = yt_video.url.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().default_filename
    #     if ".mp4" in yt_vid_name:
    #         yt_vid_name = yt_vid_name.replace('.mp4', "")
    #     return JsonResponse({"data": data.decode('utf8'), "filename": yt_vid_name, "mimetype": "video/mp4"}) 
        
# return JsonResponse({"download_url": yt_video.url.streams.get_by_itag(vid_id).url})
    
    