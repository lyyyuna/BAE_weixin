#-*- coding:utf-8 -*-
#! /usr/bin/env python
# coding=utf-8
__author__ = 'lyyyuna'
from bottle import *
import hashlib
import xml.etree.ElementTree as ET
import urllib2
# import requests
import json
 
@get("/")
def checkSignature():
    token = "sugar"  
    signature = request.GET.get('signature', None)
    timestamp = request.GET.get('timestamp', None)
    nonce = request.GET.get('nonce', None)
    echostr = request.GET.get('echostr', None)
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return echostr
    else:
        return None
 

# Mod WSGI launch
from bae.core.wsgi import WSGIApplication

app = default_app()
application = WSGIApplication(app)