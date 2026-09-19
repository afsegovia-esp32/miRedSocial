from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'chat'

urlpatterns = [
    path("", chat_page, name='chat_page')
]