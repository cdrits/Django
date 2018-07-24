from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("<h1>Rango says hey there partner!</h1>"
                        "<br><a href='/rango/about/'> About </a>")


def about(request):
    return HttpResponse("<h1>Rango says this is the ABOUT page!</h1>"
                        "<br><a href='/rango/'> Index </a>")
