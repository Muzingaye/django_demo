import logging
import os
from django.conf import settings
from django.views.static import serve
from django.http import FileResponse, HttpResponse, HttpRequest, JsonResponse

from django.shortcuts import render


def home(request):
    pass
