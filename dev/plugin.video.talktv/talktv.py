from __future__ import unicode_literals
# -*- coding: utf-8 -*- 
__author__ = 'MrOdin'
import urllib, urllib2, re, os, sys, StringIO, gzip
import xbmc
import json
import xbmcaddon,xbmcplugin,xbmcgui
import requests
import urlparse
from bs4 import BeautifulSoup,NavigableString
# import BeautifulSoup

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')

SETTING = xbmcaddon.Addon(id=ADDON_ID)

mHOME=0
mALL_CHANNEL=100
mALL_GAME=200
mGAME=300
def load(url):
	r = requests.get(url)
	return r.text
def getVideoLink(url):
	sp = url.split('/')
	sid = sp[len(sp)-1]
	return 'http://localhost:9998/TalkTV?sid='+sid
def addItems(items):
	listitems = range(len(items))
	for i, item in enumerate(items):
		listItem = xbmcgui.ListItem(label=item["label"], label2=item["label2"], iconImage=item["icon"], thumbnailImage=item["thumb"])
		if item.get("info"):
				listItem.setInfo("video", item["info"])
		if item.get("stream_info"):
				for type_, values in item["stream_info"].items():
						listItem.addStreamInfo(type_, values)
		if item.get("art"):
				listItem.setArt(item["art"])
		if item.get("context_menu"):
				listItem.addContextMenuItems(item["context_menu"])
		listItem.setProperty("isPlayable", item["playable"] and "true" or "false")
		if item.get("properties"):
				for k, v in item["properties"].items():
						listItem.setProperty(k, v)
		listitems[i] = (item["path"], listItem, not item["playable"])

	xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
	xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

def makeFolderItem(label,url,m):
	return {'label':label,'label2':'','icon':'DefaultFolder.png','thumb':'','playable':False,'path':buildPath({'url':url,'m':m})}

def parseQs(qs):
    param=[]
    paramstring=qs
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=urllib.unquote_plus(splitparams[1])
    return param

def buildPath(d):
	url = sys.argv[0]+'?'
	for key, value in d.iteritems():
		url = url + '%s=%s&'%(key,urllib.quote_plus(str(value)))
	return url
def parse(url,mode):
	if mode == None or mode == mHOME:
		return parseHome()
	if mode == mALL_CHANNEL:
		return parseAllChannel(url)
	if mode == mALL_GAME:
		return parseAllGame(url)
	if mode == mGAME:
		return parseGame(url)
	return []
def parseHome():
	items = []
	items.append(makeFolderItem(u'Kênh','http://talktv.vn/browse/channels',mALL_CHANNEL))
	items.append(makeFolderItem(u'Game','http://talktv.vn/browse/games/ajax-get-games/0',mALL_GAME))
	return items

def parseAllGame(url):
	html = load(url)
	soup = BeautifulSoup(html)
	items = soup.select('div.cellitem')
	r = []
	for item in items:
		title = item.select('p.gamename a')[0].get_text()
		thumb = item.select('img')[0]['src']
		#http://talktv.vn/browse/channels/112/Liên Minh Huyền Thoại
		href = item.select('p.gamecover a')[0]['href']
		href = href[0:href.rfind('/')+1]
		viewers = item.select('span.gameviewer')[0].get_text()

		r.append({'label':title,'label2':viewers,'icon':thumb,'thumb':thumb,'playable':False,'path':buildPath({'url':href,'m':mGAME})})

	more = soup.select('div.browse-loadmore')
	if len(more)>0:
		#onclick="gamesBrowse.loadMoreGame(1)"
		onclick = more[0]['onclick']
		onclick = onclick.replace('gamesBrowse.loadMoreGame(','').replace(')','')
		nextPUrl = 'http://talktv.vn/browse/games/ajax-get-games/'+onclick

		r.append({'label':'Next Page','label2':'','icon':'DefaultFolder.png','thumb':'DefaultFolder.png','playable':False,'path':buildPath({'url':nextPUrl,'m':mALL_GAME})})
	return r
	
def parseGame(url):
	return parseAllChannel(url)

def parseAllChannel(url):
	html = load(url)
	soup = BeautifulSoup(html)
	items = soup.select('div.cellitem')
	r  = []
	for item in items:
		a = item.select("p.txtname a")[0]
		title = a.get_text().strip()
		href = a['href']
		img = item.select('span.thumbnail img')[0]
		thumb = img['src']	
		game = item.select('p.txtgamename a')[0].get_text()
		streamer = item.select('a.username')[0].get_text().replace('\n','').strip().encode('utf-8')
		href =getVideoLink(href)
		r.append({'label':streamer + ' - ' + title,'label2':game,'icon':thumb,'thumb':thumb,'playable':True,'path':href})
	return r
	
SYSARG=str(sys.argv[1])

HANDLE = int(sys.argv[1])
PARAMS = parseQs(sys.argv[2])

xbmcplugin.setContent(HANDLE, 'movies')

url = None
mode = None
if 'url' in PARAMS:
	url = PARAMS['url']
if 'm' in PARAMS:
	mode = int(PARAMS['m'])

items = parse(url,mode)
if items != None:
	addItems(items)