from django.shortcuts import render
from .main import *

def home(reqest):
    Main().start_trade()
    return render(reqest, 'base.html')