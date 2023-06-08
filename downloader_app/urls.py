from django.contrib import admin
from django.urls import path, include
from downloader_app import views

urlpatterns = [
    path('', views.index, name="index"),
    path('vid_detail', views.get_vid_details, name="get_vid_details"),
    path('download_vid', views.download_vid, name="download_video"),
    
]