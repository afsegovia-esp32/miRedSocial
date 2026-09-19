from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'posts'

urlpatterns = [
    path("feed/", feed_page, name='feed_page')
]