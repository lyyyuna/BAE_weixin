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
 
def parse_msg():
    recvmsg = request.body.read()
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg 
 
 
def query_movie_info():
    movieurlbase = "http://api.douban.com/v2/movie/search"
    DOUBAN_APIKEY =  "08cbc4f981e88c301a634eec85b9a490"  # 这里需要填写你自己在豆瓣上申请的应用的APIKEY
    movieinfo = parse_msg()
    searchkeys = urllib2.quote(movieinfo["Content"].encode("utf-8"))  # 如果Content中存在汉字，就需要先转码，才能进行请求
    url = '%s?q=%s&apikey=%s' % (movieurlbase, searchkeys, DOUBAN_APIKEY)
    # return "<p>{'url': %s}</p>" % url
    # url = '%s%s?apikey=%s' % (movieurlbase, id["Content"], DOUBAN_APIKEY)
    # resp = requests.get(url=url, headers=header)
    resp = urllib2.urlopen(url)
    movie = json.loads(resp.read())
    # return "<p>{'movie': %s}</p>" % movie
    # info = movie["subjects"][0]["title"] + movie["subjects"][0]["alt"]
    # info = movie['title'] + ': ' + ''.join(movie['summary'])
    return movie
    # return info
 
def query_movie_details():
    movieurlbase = "http://api.douban.com/v2/movie/subject/"
    DOUBAN_APIKEY =  "08cbc4f981e88c301a634eec85b9a490"  # 这里需要填写你自己在豆瓣上申请的应用的APIKEY
    id = query_movie_info()
    url = '%s%s?apikey=%s' % (movieurlbase, id["subjects"][0]["id"], DOUBAN_APIKEY)
    resp = urllib2.urlopen(url)
    description = json.loads(resp.read())
    description = ''.join(description['summary'])
    return description 
 
 
@post("/")
def response_msg():

    msg = parse_msg()

    textTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[%s]]></MsgType>
             <Content><![CDATA[%s]]></Content>
             <FuncFlag>0</FuncFlag>
             </xml>"""

    pictextTpl = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[news]]></MsgType>
                <ArticleCount>1</ArticleCount>
                <Articles>
                <item>
                <Title><![CDATA[%s]]></Title>
                <Description><![CDATA[%s]]></Description>
                <PicUrl><![CDATA[%s]]></PicUrl>
                <Url><![CDATA[%s]]></Url>
                </item>
                </Articles>
                <FuncFlag>1</FuncFlag>
                </xml> """

    if msg["MsgType"] == "event":
        echostr = textTpl % (
            msg['FromUserName'], msg['ToUserName'], str(int(time.time())), msg['MsgType'],
            u"欢迎关注豆瓣电影，输入电影名称即可快速查询电影讯息哦！")
        return echostr
    else:
        Content = query_movie_info()
        description = query_movie_details()
        echostr = pictextTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                                Content["subjects"][0]["title"], description,
                                Content["subjects"][0]["images"]["large"], Content["subjects"][0]["alt"])
        return echostr


# Mod WSGI launch
from bae.core.wsgi import WSGIApplication

app = default_app()
application = WSGIApplication(app)