from __future__ import unicode_literals
# -*- coding: utf-8 -*- 
__author__ = 'MrOdin'
import urllib, urllib2, re, os, sys, StringIO
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
QUALITY = int(SETTING.getSetting('video_quality'))
VIDEO_INFO_API='http://api.tv.zing.vn/2.0/media/info?api_key=d04210a70026ad9323076716781c223f&session_key=91618dfec493ed7dc9d61ac088dff36b&&media_id='
THUMB_BASE_URL = 'http://image.mp3.zdn.vn/'
HOME_URL = 'http://tv.zing.vn'
mHOME =0
mTHE_LOAI=100
mTHE_LOAI_CON=101
mTHE_LOAI_NOI_BAT=102
mTHE_LOAI_NOI_BAT_CON=103
mSERIES=200
mCHANNEL=300
MPLAY=1000

def getVideoId(href):
	sp = href.split('/')
	sid = sp[len(sp)-1].replace('.html','').replace('.htm','')
	return sid
def getZingTvUrl(href):
	sid = getVideoId(href)
	sUrl =  'http://localhost:9998/ZingTV?sid='+sid +'&q='+str(QUALITY)
	return sUrl
def checkUrl(url):
	try:
		ret = urllib2.urlopen(url)
		code = ret.code
		#log('check url:%s - %d'%(url,code))
		return ret.code < 400
	except Exception, e:
		#log('check url:%s - %s'%(url,str(e)))
		return False
		pass
def getSource(source,quality=3):
	result = None

	if quality <0 :
		return result

	ss = []
	if 'Video3GP' in source:
		ss.append('http://'+source['Video3GP'])
	else:
		ss.append(None)

	if 'Video480' in source:
		ss.append('http://'+source['Video480'])
	else:
		ss.append(None)

	if 'Video720' in source:
		ss.append('http://'+source['Video720'])
	else:
		ss.append(None)

	if 'Video1080' in source:
		ss.append('http://'+source['Video1080'])
	else:
		ss.append(None)
	if ss[quality]!=None:
		result = ss[quality]
	else:
		for i in range(quality,-1,-1):
			if ss[i] != None:
				result = ss[i]
				break
		if result == None:
			for i in range(quality,len(ss)):
				if ss[i] != None:
					result = ss[i]
					break

	if result !=None and checkUrl(result):
		return result
	else:
		return getSource(source,quality-1)

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
def pagination(soup,mode):
	pages = soup.select('ul.pagination a')

	for i in range(0,len(pages)-1):
		page = pages[i]
		cls = page.get('class')
		if cls != None and len(cls)>0 and cls[0] == 'active':
			nextPage= pages[i+1]
			href = HOME_URL + nextPage.get('href')
			return makeFolderItem(u'Next Page',href,mode)
	return None
def alert(msg):
	xbmcgui.Dialog().ok(addonName, msg)
	pass

def load(url):
	r = requests.get(url)

	return r.text
def parse(url,mode):
	if mode == mHOME:
		return parseHome()
	if mode == mTHE_LOAI:
		return parseTheLoai(url)
	if mode == mTHE_LOAI_NOI_BAT:
		return parseTheLoaiNoiBat(url)
	if mode == mTHE_LOAI_NOI_BAT_CON:
		return parseTheLoaiNoiBatCon(url,int(PARAMS['section']))
	if mode == mTHE_LOAI_CON:
		return parseTheLoaiCon(url)
	if mode == mCHANNEL:
		return parseChannel(url)
	if mode == mSERIES:
		return parseSeries(url)
	if mode ==MPLAY:
		play(url)
	return None
def makeFolderItem(label,url,m):
	return {'label':label,'label2':'','icon':'DefaultFolder.png','thumb':'','playable':False,'path':buildPath({'url':url,'m':m})}

def parseHome():
	items = []
	items.append(makeFolderItem(u'TV show','http://tv.zing.vn/the-loai/TV-Show/IWZ9Z0CE.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Phim truyền hình','http://tv.zing.vn/the-loai/Phim/IWZ9Z0DW.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Phim hoạt hình','http://tv.zing.vn/the-loai/Hoat-Hinh/IWZ9Z0DO.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Hài hước','http://tv.zing.vn/the-loai/Hai-Huoc/IWZ9Z0D6.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Thiếu nhi','http://tv.zing.vn/the-loai/Thieu-Nhi/IWZ9ZIW8.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Khoa học - Giáo dục','http://tv.zing.vn/the-loai/Giao-Duc/IWZ9Z0D7.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Phim điện ảnh','http://tv.zing.vn/the-loai/Phim-Dien-Anh/IWZ9ZIOZ.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Âm nhạc','http://tv.zing.vn/the-loai/Am-nhac/IWZ9Z0DC.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Tin tức - Thời sự','http://tv.zing.vn/the-loai/Tin-Tuc-Su-Kien/IWZ9Z0CF.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Thể thao','http://tv.zing.vn/the-loai/The-Thao/IWZ9Z0DI.html',mTHE_LOAI))
	return items
def parseTheLoai(url):
	html = load(url)
	soup = BeautifulSoup(html)
	container = soup('div',{'class':'dropdown'})
	container = container[len(container)-1]
	links  = container.select('a')
	items = []
	noibat = u'Nổi Bật'
	for link in links:
		title = link.get_text()
		if title == noibat:
			m = mTHE_LOAI_NOI_BAT
		else:
			m = mTHE_LOAI_CON
		item = makeFolderItem(title,HOME_URL+ link['href'],m)
		items.append(item)
	return items
def parseTheLoaiCon(url):
	html = load(url)
	soup = BeautifulSoup(html)
	result = []
	items = soup.select('div.item')
	for item in items:
		title = item.select('div.box-description h3 a')[0].get_text()
		thumb = item.select('a.thumb img')[0]['src']
		link = buildPath({'url':HOME_URL+ item.select('a.thumb')[0]['href'],'m':mCHANNEL})
		rate = item.select('div.rating-score span')[0].get_text()

		views = item.select('span._listen')[0].get_text()
		tagline = item.select('p')[0].get_text()
		r = {'label':title,'label2':rate+'/'+views,'icon':thumb,'thumb':thumb,'playable':False,'path':link}
		r['art'] = {'thumb':thumb,'poster':thumb,'fanart':thumb}
		r['info'] = {'title':title,'tagline':tagline,'Plot':tagline,'plotoutline':tagline,'playcount':views,'Rating':float(rate),'watched':views}
		result.append(r)
	p = pagination(soup,mTHE_LOAI_CON)

	if p!=None:
		result.append(p)

	return result
def parseChannel(url):
	html = load(url)
	soup = BeautifulSoup(html)
	result = []
	series = soup.select('div.section')
	for s in series:
		if 'row' in str(s['class']):
			title = s.select('div.title-bar h3')[0].get_text()

def parseSeries(url):
	print url
	xbmcplugin.setContent(HANDLE, 'episode')

	if not 'series' in url:
		html = load(url)
		soup = BeautifulSoup(url)
		seeAll = soup.select('div.see-all a')
		url  = HOME_URL+ seeAll[1]['href']

	html = load(url)
	soup = BeautifulSoup(html)
	result =[]
	items = soup.select('div.item')
	for item in items:
		title = item.select('div.box-description h3 a')[0].get_text()
		thumb = item.select('a.thumb img')[0]['src']
		#link = getVideoUrl(item.select('a.thumb')[0]['href'])
		#link = buildPath({'url':item.select('a.thumb')[0]['href'],'m':MPLAY})
		link = getZingTvUrl(item.select('a.thumb')[0]['href'])
		rate = item.select('div.rating-score span')[0].get_text()
		name = item.select('div.info-detail a')[0].get_text()
		title = name+" - "+title
		views = item.select('span._listen')[0].get_text()

		r = {'label':title,'label2':rate+'/'+views,'icon':thumb,'thumb':thumb,'playable':True,'path':link}
		r['art'] = {'thumb':thumb,'poster':thumb,'fanart':thumb}
		r['info'] = {'title':title,'playcount':views,'Rating':float(rate),'watched':views}
		result.append(r)
	p = pagination(soup,mSERIES)
	if p!=None:
		result.append(p)
	return result
def parseTheLoaiNoiBat(url):
	html = load(url)
	soup = BeautifulSoup(html)
	sections = soup.select('div.section')
	section = 0
	results = []
	for s in sections:
		print s['class']
		if 'row' in str(s['class']):
			title = s.select('div.title-bar h3')[0].get_text()
			link = buildPath({'url':url,'m':mTHE_LOAI_NOI_BAT_CON,'section':section})
			results.append({'label':title,'label2':'','icon':'DefaultFolder.png','thumb':'','playable':False,'path':link})
			section = section+1
	return results
def parseTheLoaiNoiBatCon(url,section):
	html = load(url)
	soup = BeautifulSoup(html)
	sections = soup.select('div.section')
	s = sections[section]
	items = s.select('div.item')
	result = []
	for item in items:
		aT = item.select('h4.title a')
		if len(aT)>0:
			title = aT[0].get_text()
		else:
			aT = item.select('h3 a._trackLink')
			if len(aT)>0:
				title = aT[0].get_text()

		subT =item.select('h5.subtitle a')

		if len(subT)>0:
			title = title + ' '+subT[0].get_text()
		
		#href  =  buildPath({'url':a['href'],'m':MPLAY})
		playable = False
		href = aT[0]['href']
		if '.html' in href:
			playable = True
			href = getZingTvUrl(aT[0]['href'])
		else:
			href = buildPath({'url':href,'m':mSERIES})
		thumb = item.a.img['_src']

		result.append({'label':title,'label2':'','icon':thumb,'thumb':thumb,'playable':playable,'path':href})
	return result
def play(url):
	sid = getVideoId(url)
	url = VIDEO_INFO_API + sid
	r = json.loads(load(url))['response']
	title = r['full_name']
	thumb = THUMB_BASE_URL + r['thumbnail']
	seriesThumb = THUMB_BASE_URL + r['program_thumbnail']
	source = getSource(r['other_url'],QUALITY)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	listitem = xbmcgui.ListItem(label = title,iconImage = seriesThumb,thumbnailImage = thumb )
	listitem.setInfo('video', {'Title': title})
	player.play(source,listitem)

SYSARG=str(sys.argv[1])

HANDLE = int(sys.argv[1])
PARAMS = parseQs(sys.argv[2])


xbmcplugin.setContent(HANDLE, 'movies')

url = HOME_URL
mode = mHOME

if 'url' in PARAMS:
	url = PARAMS['url']
if 'm' in PARAMS:
	mode = int(PARAMS['m'])

items = parse(url,mode)
if items != None:
	addItems(items)
