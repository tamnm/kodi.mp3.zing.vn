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
QUALITY = int(SETTING.getSetting('video_quality'))
VIDEO_INFO_API='http://api.tv.zing.vn/2.0/media/info?api_key=d04210a70026ad9323076716781c223f&session_key=91618dfec493ed7dc9d61ac088dff36b&&media_id='
THUMB_BASE_URL = 'http://image.mp3.zdn.vn/'
HOME_URL = 'http://tv.zing.vn'

SEARCH_CHANNEL_URL = 'http://tv.zing.vn/tim-kiem/program.html?q='
SEARCH_VIDEO_URL = 'http://tv.zing.vn/tim-kiem/video.html?q='

mHOME =0
mTHE_LOAI=100
mTHE_LOAI_CON=101
mTHE_LOAI_NOI_BAT=102
mTHE_LOAI_NOI_BAT_CON=103
mSERIES=200
mCHANNEL=300
mCHANNEL_SECTION=301
mPHIM =400
mSEARCH = 500
mSEARCH_CHANNEL=501
mSEARCH_VIDEO=502
mSEARCH_MV=503
MPLAY=1000


def getUserInput():
	keyb = xbmc.Keyboard('', 'Enter keyword')
	keyb.doModal()
	searchText = None
	if (keyb.isConfirmed()):
		searchText = urllib.quote_plus(keyb.getText())
	return searchText

def fixZingLink(href):
	if not 'http' in href:
		return HOME_URL + href
	return href
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
			href = fixZingLink(nextPage.get('href'))
			return makeFolderItem(u'Next Page',href,mode)
	return None
def alert(msg):
	xbmcgui.Dialog().ok(ADDON_NAME, msg)
	pass

def load(url):
	header = {'Connection': 'keep-alive','Accept-Encoding': 'gzip, deflate','Accept': '*/*','User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
	#r = requests.get(url)
	#print r.headers
	#return r.text
	request = urllib2.Request(url,headers = header)
	#request.add_header('Accept-encoding', 'gzip')
	response = urllib2.urlopen(request)
	data = response.read()
	print response.info()
	if response.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(data)
		f = gzip.GzipFile(fileobj=buf)
		data = f.read()
	return data
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
	if mode == mCHANNEL_SECTION:
		return parseChannelSection(url,int(PARAMS['section']))
	if mode == mPHIM:
		return phim(url)
	if mode == mSERIES:
		return parseSeries(url)
	if mode == mSEARCH:
		return search(url)
	if mode == mSEARCH_CHANNEL:
		return searchChannel(url)
	if mode == mSEARCH_VIDEO:
		return searchVideo(url)
	if mode == mSEARCH_MV:
		return searchMV(url)
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
	#items.append(makeFolderItem(u'Phim điện ảnh','http://tv.zing.vn/the-loai/Phim-Dien-Anh/IWZ9ZIOZ.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Âm nhạc','http://tv.zing.vn/the-loai/Am-nhac/IWZ9Z0DC.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Tin tức - Thời sự','http://tv.zing.vn/the-loai/Tin-Tuc-Su-Kien/IWZ9Z0CF.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Thể thao','http://tv.zing.vn/the-loai/The-Thao/IWZ9Z0DI.html',mTHE_LOAI))
	items.append(makeFolderItem(u'Tìm kiếm','',mSEARCH))
	return items
def parseTheLoai(url):
	load('http://localhost:8080/test.php')
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
		item = makeFolderItem(title,fixZingLink(link['href']),m)
		items.append(item)
	return items
def parseSingleChannel(item):
	title = item.select('div.box-description h3 a')[0].get_text()
	thumb = item.select('a.thumb img')[0]['src']
	
	m = mCHANNEL
	playable = False
	href = item.select('a.thumb')[0]['href']

	if 'phim' in href:
		m = mPHIM
	link = buildPath({'url':fixZingLink(href),'m':m})

	rate = item.select('div.rating-score span')[0].get_text()

	views = item.select('span._listen')[0].get_text()
	p = item.select('p')
	tagline = ''
	if len(p)>0:
		tagline = p[0].get_text()

	r = {'label':title,'label2':rate+'/'+views,'icon':thumb,'thumb':thumb,'playable':playable,'path':link}
	r['art'] = {'thumb':thumb,'poster':thumb,'fanart':thumb}
	r['info'] = {'title':title,'tagline':tagline,'Plot':tagline,'plotoutline':tagline,'playcount':views,'Rating':float(rate),'watched':views}
	return r
def parseTheLoaiCon(url):
	html = load(url)
	soup = BeautifulSoup(html)
	result = []
	items = soup.select('div.item')
	for item in items:
		result.append(parseSingleChannel(item))

	p = pagination(soup,mTHE_LOAI_CON)

	if p!=None:
		result.append(p)

	return result
def parseChannel(url):
	html = load(url)
	soup = BeautifulSoup(html)
	result = []
	series = soup.select('div.section')
	section =0
	for s in series:
		if 'row' in str(s['class']):
			h3 = s.select('div.title-bar h3')[0]
			title = h3.get_text()
			href = url
			a = h3.select('a')
			m = mCHANNEL_SECTION
			if len(a)>0:
				href = fixZingLink(a[0]['href'])
				m = mSERIES
			
			link = buildPath({'url':href,'m':m,'section':section})
			result.append({'label':title,'label2':'','icon':'DefaultFolder.png','thumb':'','playable':False,'path':link})
		section = section+1
	return result
def phim(url):
	return []
	#html = load(url)
	#soup = BeautifulSoup(html)
	#buttons = soup.select('div.button-list a')
	#result = []
	#for a in buttons:
	#	title = a.get_text()
	#	href = a['href']
	#	if 'Xem' in title:
	#		link = getZingTvUrl(href)
	#		result.append({'label':title,'label2':'','icon':'DefaultVideo.png','thumb':'','playable':True,'path':link})
	#return result
def parseChannelSection(url,section):
	print url
	html = load(url)
	soup = BeautifulSoup(html)
	result = []
	s = soup.select('div.section')[section]
	items = s.select('div.item')
	for item in items:
		a = item.select('.title a')[0]
		title = a.get_text()
		#href= HOME_URL + a['href']
		href = getZingTvUrl(a['href'])

		thumb = item.select('img')[0]['_src']
		result.append({'label':title,'label2':'','icon':thumb,'thumb':thumb,'playable':True,'path':href})
	return result
	
def parseSeries(url):
	print url
	xbmcplugin.setContent(HANDLE, 'episode')

	#if not 'series' in url:
	#	html = load(url)
	#	soup = BeautifulSoup(url)
	#	seeAll = soup.select('div.see-all a')
	#	url  = HOME_URL+ seeAll[1]['href']

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
		
		aname =item.select('div.info-detail a')
		if len(aname) >0:
			title  = aname[0].get_text()+" - "+title

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
			href = fixZingLink(href)
			href = buildPath({'url':href,'m':mCHANNEL})
		thumb = item.a.img['_src']

		result.append({'label':title,'label2':'','icon':thumb,'thumb':thumb,'playable':playable,'path':href})
	return result
def search(url):
	items =[]
	items.append(makeFolderItem(u'Tìm kiếm Chương trình','',mSEARCH_CHANNEL))
	items.append(makeFolderItem(u'Tìm kiếm Video','',mSEARCH_VIDEO))
	items.append(makeFolderItem(u'Tìm kiếm MV','',mSEARCH_MV))
	return items
def searchChannel(url):
	if url == None or url == '':
		kw = getUserInput()
		url  = SEARCH_CHANNEL_URL + kw
	return parseTheLoaiCon(url)
def searchVideo(url):
	if url == None or url == '':
		kw = getUserInput()
		url  = SEARCH_VIDEO_URL + kw
	return parseSeries(url)
def searchMV(url):
	if url == None or url == '':
		kw = getUserInput()
		url  = SEARCH_VIDEO_URL + kw
	return parseSeries(url)
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

url = ''
mode = mHOME

if 'url' in PARAMS:
	url = PARAMS['url']
if 'm' in PARAMS:
	mode = int(PARAMS['m'])

items = parse(url,mode)
if items != None:
	addItems(items)
