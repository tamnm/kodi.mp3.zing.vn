from __future__ import unicode_literals
# -*- coding: utf-8 -*- 
__author__ = 'MrOdin'
import urllib, urllib2, re, os, sys, StringIO
import xbmc
import json
import xbmcaddon,xbmcplugin,xbmcgui
import requests
import xbmcgui

from bs4 import BeautifulSoup,NavigableString
addon = xbmcaddon.Addon()
addonId = addon.getAddonInfo('id')
addonName = addon.getAddonInfo('name')

mysettings = xbmcaddon.Addon(id=addonId)

video_quality = int(mysettings.getSetting('video_quality'))
audio_quality = int(mysettings.getSetting('audio_quality'))

thumbBaseUrl = 'http://image.mp3.zdn.vn'

homeUrl = 'http://mp3.zing.vn'

searchSongUrl = 'http://mp3.zing.vn/tim-kiem/bai-hat.html?q='
searchAlbumUrl = 'http://mp3.zing.vn/tim-kiem/playlist.html?q='
searchVideoUrl = 'http://mp3.zing.vn/tim-kiem/video.html?q='
searchArtistUrl = 'http://ac.mp3.zing.vn/complete?type=artist&query='
artistInfoApi =  'http://api.mp3.zing.vn/api/mobile/artist/getartistinfo?key=fafd463e2131914934b73310aa34a23f&requestdata={"id":"_ID_"}'
topApi ='http://mp3.zing.vn/xhr/song?op=get-top&start=0&length=100&id='

mHome=0
mAllChuDe=100
mChuDe=101
mAllVideo=200
mVideoChuDe=201

mAllNgheSy=300
mNgheSy=301
mNgheSySongs=302
mNgheSyAlbum=303
mNgheSyVideo=304
mNgheSyRadio=305

mAllBxh=400
mBxhSong=401
mBxhAlbum=402
mBxhMv=403
mAllTop100=500
mTop100Sub=501
mTop100Song=502
mAllAlbum=600
mAlbum=601
mAlbumChuDe=602
mSearch=700
mSearchSong=701
mSearchAlbum=702
mSearchMv=703

mHot=800
mHotAlbum=801
mHotMV=802
mHotViet=803
mHotVietNew=804
mHotPlaylist=805

mPlaySong=1000
mPlayAllAlbum=1001
mPlayAllVideoChuDe=1002
mPlayAllBxhSong=1003
mPlayAllBxhMv=1004
mPlayAllSearchSong=1005
mPlayAllNgheSySongs=1006
mPlayAllNgheSyVideo=1007
mPlayAllSearchVideo=1008

mPlayAllHotMV=1009
mPlayAllHotViet=1010
mPlayAllHotVietNew=1011
mPlayAllTop100Song=1012

def getSongUrl(href):
	sid = getSongId(href)
	sUrl =  'http://localhost:9998/mp3ZAudio?sid='+sid +'&q='+str(audio_quality)
	return sUrl
def getVideoUrl(href):
	sid = getSongId(href)
	sUrl =  'http://localhost:9998/mp3ZVideo?sid='+sid +'&q='+str(video_quality)
	return sUrl
def getSongId(href):
	sp = href.split('/')
	sid = sp[len(sp)-1].replace('.html','').replace('.htm','')
	return sid
def alert(msg):
	xbmcgui.Dialog().ok(addonName, msg)
	pass
def load(url):
	r = requests.get(url)
	return r.text
def addVideo(title,url,thumb,artist,icon='DefaultVideo.png',duration=None,commands=None):
	title = title.encode('utf-8')
	artist = artist.encode('utf-8')

	li = xbmcgui.ListItem(title, iconImage=icon,thumbnailImage=thumb)
	infoLabels = {'Artist':[artist],'Title':title}
	
	if duration!=None:
		infoLabels['Duration']=duration
	
	li.setInfo(type='Video',infoLabels=infoLabels)
	li.setProperty("IsPlayable","true")
	
	if commands!= None:
		li.addContextMenuItems(commands,replaceItems=False)

	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)	
	pass

def albumCommand(url):
	return createCommand('Play Album',url,mPlayAllAlbum)

def createCommand(text,url,mode):
	commands = []
	script = 'XBMC.Container.Update(plugin://%s?url=%s&mode=%d)'%(addonId,urllib.quote_plus(url),mode)
	commands.append((text, script))
	return commands

def addSong(title,url,thumb,artist,icon='DefaultAudio.png',commands=None):
	title = title.encode('utf-8')
	artist = artist.encode('utf-8')

	li = xbmcgui.ListItem(artist +u' - '.encode('utf-8')+ title, iconImage=icon,thumbnailImage=thumb)
	infoLabels = {'Artist':artist,'Title':title},

	li.setProperty("IsPlayable","true")
	li.setProperty("mimetype","audio/mpeg")
	li.setLabel2(artist)

	if commands!= None:
		li.addContextMenuItems(commands,replaceItems=False)

	li.setInfo(type='Music',infoLabels=infoLabels)
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
	return li

def addDir(name,url,mode,thumb='DefaultFolder.png',commands=None,art=None,params=''):
	url = url.encode('utf-8')
	name = name.encode('utf-8')
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+params
	liz=xbmcgui.ListItem(name,iconImage=thumb,thumbnailImage=thumb)
	liz.setInfo( type="Songs", infoLabels={ "Title": name} )

	if art!=None:
		liz.setArt(art)
		liz.setProperty('fanart_image',art)

	if commands!= None:
		liz.addContextMenuItems(commands,replaceItems=False)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

	return liz
def get_params():
        param=[]
        paramstring=sys.argv[2]
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
                                param[splitparams[0]]=splitparams[1]

        return param
def home():
	addDir(u'Hot','',mHot)
	addDir(u'Chủ đề',"http://mp3.zing.vn/chu-de",mAllChuDe)
	addDir(u'Album','http://mp3.zing.vn/the-loai-album.html',mAllAlbum)
	addDir(u'Video','http://mp3.zing.vn/the-loai-video.html',mAllVideo)
	addDir(u'Bảng xếp hạng','http://mp3.zing.vn/bang-xep-hang/index.html',mAllBxh)
	addDir(u'Nghệ sỹ','',mAllNgheSy)
	addDir(u'Tìm kiếm','',mSearch)
	addDir(u'Top100','',mAllTop100)
	pass
def allChuDe(url):
	html = load(url)
	soap = BeautifulSoup(html)('a',{'class':'txt-title-lagre'})
	for a in soap:
		title = a['title']
		href = a['href']
		href = href +'?view=playlist'
		addDir(title,href,mChuDe)
	pass
def chuDe(url):
	html = load(url)
	soup = BeautifulSoup(html)
	albums  = soup('a',{'class':'thumb'})
	for a in albums:
		href = a['href']
		title = a['title']
		thumb = a('img')[0]['src']
		commands = albumCommand(href)
		addDir(title,href,mAlbum,thumb,commands= commands)
	pass
def getAlbumSongs(url):
	html = load(url)
	soup = BeautifulSoup(html)
	player = soup('div',{'id':'html5player'})[0]
	xmlUrl = player['data-xml']
	xmlUrl = xmlUrl.replace('/xml/','/html5xml/')
	xml = load(xmlUrl)
	js = json.loads(xml)
	songs=[]
	for s in js['data']:
		href = s['link']
		title = s['name']
		artist = s['artist']
		thumb=thumbBaseUrl+ s['cover']
		
		songs.append({'Title':title,'Artist':artist,'Thumb':thumb,'Link':href})
	return songs
def album(url):
	songs = getAlbumSongs(url)
	commands = albumCommand(url)
	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = commands)
	pass
def playAllAlbum(url):
	songs = getAlbumSongs(url)
	playAllSong(songs)

def allAlbum(url):
	html = load(url)
	soup = BeautifulSoup(html)
	ul = soup.select('ul.data-list')[1]
	
	for li in ul.contents:
		if hasattr(li,'name'):
			pre = li.a.string +"-"
			for sli in li.ul.contents:
				if hasattr(sli,'name'):
					href = sli.a['href']
					title = pre+ sli.a.string
					addDir(title,href,mAlbumChuDe)
	pass
def albumChuDe(url):
	xbmc.executebuiltin('Container.SetViewMode(%d)'%(500))
	html = load(url)
	soup = BeautifulSoup(html)
	items = soup.select('div.item')
	for item in items:
		a = item.a
		title = a['title']
		href = a['href']
		thumb = a.img['src']
		addDir(title,href,mAlbum,thumb)
	pagination(soup,mAlbumChuDe)
def pagination(soup,mode):
	pages = soup.select('div.pagination a')

	for i in range(0,len(pages)-1):
		page = pages[i]
		cls = page.get('class')
		if cls != None and len(cls)>0 and cls[0] == 'active':
			nextPage= pages[i+1]
			href = homeUrl + nextPage.get('href')
			addDir('Next Page',href,mode)
			break
def allVideo(url):
	html = load(url)
	soup = BeautifulSoup(html)
	ul = soup.select('ul.data-list')[1]
	
	for li in ul.contents:
		if hasattr(li,'name'):
			pre = li.a.string +"-"
			for sli in li.ul.contents:
				if hasattr(sli,'name'):
					href = sli.a['href']
					title = pre+ sli.a.string
					addDir(title,href,mVideoChuDe)
	pass
def getVideoChuDe(soup):
	items = soup.select('div.item')
	songs = []
	for item in items:
		a = item.a
		des = item.div.select('a')
		title = des[0].get_text()
		artist = des[1].get_text()
		href = a['href']
		thumb = a.img['src']
		songs.append({'Title':title,'Artist':artist,'Link':href,'Thumb':thumb})
	return songs
def videoChuDe(url):
	xbmc.executebuiltin('Container.SetViewMode(%d)'%(500))
	html = load(url)
	soup = BeautifulSoup(html)
	songs = getVideoChuDe(soup)

	cmd = createCommand('Play all video',url,mPlayAllVideoChuDe)

	for s in songs:
		addVideo(s['Title'],getVideoUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands= cmd)

	pagination(soup,mVideoChuDe)
	pass
def playAllVideoChuDe(url):
	soup = BeautifulSoup(load(url))
	songs = getVideoChuDe(soup)
	playAllVideo(songs)
	pass

def allBxh():
	addDir(u'Bài hát - Việt nam',"http://mp3.zing.vn/bang-xep-hang/bai-hat-Viet-Nam/IWZ9Z08I.html",mBxhSong)
	addDir(u'Bài hát - Âu mỹ',"http://mp3.zing.vn/bang-xep-hang/bai-hat-Au-My/IWZ9Z0BW.html",mBxhSong)
	addDir(u'Bài hát - Hàn quốc',"http://mp3.zing.vn/bang-xep-hang/bai-hat-Han-Quoc/IWZ9Z0BO.html",mBxhSong)

	addDir(u'Album - Việt nam','http://mp3.zing.vn/bang-xep-hang/album-Viet-Nam/IWZ9Z08O.html',mBxhAlbum)
	addDir(u'Album - Âu mỹ','http://mp3.zing.vn/bang-xep-hang/album-Au-My/IWZ9Z0B6.html',mBxhAlbum)
	addDir(u'Album - Hàn quốc','http://mp3.zing.vn/bang-xep-hang/album-Han-Quoc/IWZ9Z0B7.html',mBxhAlbum)

	addDir(u'Mv - Việt nam','http://mp3.zing.vn/bang-xep-hang/video-Viet-Nam/IWZ9Z08W.html',mBxhMv)
	addDir(u'Mv - Âu mỹ','http://mp3.zing.vn/bang-xep-hang/video-Au-My/IWZ9Z0BU.html',mBxhMv)
	addDir(u'Mv - Hàn quốc','http://mp3.zing.vn/bang-xep-hang/video-Han-Quoc/IWZ9Z0BZ.html',mBxhMv)

	pass
def getBxhSongs(url):
	html = load(url)
	soup = BeautifulSoup(html)
	items = soup.select('div.e-item')
	songs = []
	for item in items:
		if not isinstance(item,NavigableString):
			thumb = item.select('img')[0]['src']
			p = item.select('a.txt-primary')[0]
			title = p.get_text()
			href = p['href']
			artist = item.select('.title-sd-item a')[0].get_text()
			songs.append({'Title':title,'Artist':artist,'Thumb':thumb,'Link':href})
	return songs
def bxhSong(url):
	songs  =getBxhSongs(url)
	cmd = createCommand('Play all',url,mPlayAllBxhSong)
	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = cmd)
	pass
def playAllVideo(songs):
	alist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	alist.clear()

	for s in songs:
		artist = s['Artist'].encode('utf-8')
		title = s['Title'].encode('utf-8')
		thumb = s['Thumb'].encode('utf-8')

		li = xbmcgui.ListItem(title, iconImage=thumb,thumbnailImage=thumb)
		infoLabels = {'Artist':[artist],'Title':title}
		
		li.setInfo(type='Video',infoLabels=infoLabels)
		li.setProperty("IsPlayable","true")

		alist.add(getVideoUrl(s['Link']),li)

	xbmc.Player().play(alist)
def playAllSong(songs):
	n = xbmc.executebuiltin('Container(0).NumItems')
	print('Container(0).NumItems:'+str(n))

	alist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	alist.clear()

	for s in songs:
		artist = s['Artist'].encode('utf-8')
		title = s['Title'].encode('utf-8')

		li = xbmcgui.ListItem(title, iconImage='DefaultAudio.png')
		infoLabels = {'Artist':[artist],'Title':title}
		
		li.setProperty("IsPlayable","true")
		li.setProperty("mimetype","audio/mpeg")

		li.setInfo(type='Music',infoLabels=infoLabels)
		alist.add(getSongUrl(s['Link']),li)

	xbmc.Player().play(alist)
def playAllBxhSong(url):
	songs  =getBxhSongs(url)
	playAllSong(songs)
	pass
def bxhAlbum(url):
	xbmc.executebuiltin('Container.SetViewMode(%d)'%(500))
	
	songs = getBxhSongs(url)
	for s in songs:
		addDir(s['Title'],s['Link'],mAlbum,s['Thumb'])
	pass
def bxhMv(url):
	xbmc.executebuiltin('Container.SetViewMode(%d)'%(500))
	songs = getBxhSongs(url)
	cmd = createCommand('Play all video',url,mPlayAllBxhMv)
	for s in songs:
		addVideo(s['Title'],getVideoUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands=cmd)
	pass
def playAllBxhMv(url):
	songs = getBxhSongs(url)
	alist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	alist.clear()

	for s in songs:
		artist = s['Artist'].encode('utf-8')
		title = s['Title'].encode('utf-8')
		thumb = s['Thumb'].encode('utf-8')

		li = xbmcgui.ListItem(title, iconImage=thumb,thumbnailImage=thumb)
		infoLabels = {'Artist':[artist],'Title':title}
		
		li.setInfo(type='Video',infoLabels=infoLabels)
		li.setProperty("IsPlayable","true")
		alist.add(getVideoUrl(s['Link']),li)

	xbmc.Player().play(alist)
	pass
def getUserInput():
	keyb = xbmc.Keyboard('', 'Enter keyword')
	keyb.doModal()
	searchText = None
	if (keyb.isConfirmed()):
		searchText = urllib.quote_plus(keyb.getText())
	return searchText
def search():
	addDir(u'Tìm kiếm bài hát','',mSearchSong)
	addDir(u'Tìm kiếm Album/Playlist','',mSearchAlbum)
	addDir(u'Tìm kiếm Video','',mSearchMv)
	pass
def getSearchSongs(soup):
	songs = soup.select('div.item-song')
	r  =[]
	for song in songs:
		a = song.select('a.txt-primary')[0]
		title = a.get_text()
		href = a['href']
		thumb= ''
		artist = ''
		r.append({'Title':title,'Link':href,'Thumb':thumb,'Artist':artist})
	return r
def searchSong(url):
	if url == None or url == '':
		kw = getUserInput()
		url = searchSongUrl+ kw

	html = load(url)
	soup = BeautifulSoup(html)
	
	songs = getSearchSongs(soup)
	cmd= createCommand('Play all',url,mPlayAllSearchSong)
	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands=cmd)

	pagination(soup,mSearchSong)
def playAllSearchSong(url):
	html = load(url)
	soup = BeautifulSoup(html)
	songs = getSearchSongs(soup)
	playAllSong(songs)
	pass
def getSearchVideos(soup):
	videos = soup.select('a.thumb')
	r  = []
	for v in videos:
		r.append({'Title':v['title'],'Link':v['href'],'Thumb':v.img['src'],'Artist':''})
	return r
def playAllSearchVideo(url):
	html = load(url)
	soup = BeautifulSoup(html)
	videos = getSearchVideos(soup)
	playAllVideo(videos)
	pass
def searchAlbum(url):
	if url == None or url == '':
		kw = getUserInput()
		url = searchAlbumUrl + kw
	html = load(url)
	soup =BeautifulSoup(html)
	items = soup.select('li.item')
	for item in items:
		a = item.select('a.thumb')[0]
		title = a['title']
		href = a['href']
		thumb = a.img['src']
		addDir(title,href,mAlbum,thumb)
	pagination(soup,mAlbumChuDe)
def searchMv(url):
	if url == None or url == '':
		kw = getUserInput()
		url = searchVideoUrl+ kw
	html = load(url)
	soup = BeautifulSoup(html)
	
	songs = getSearchVideos(soup)
	cmd = createCommand('Play all video',url,mPlayAllSearchVideo)
	for s in songs:
		addVideo(s['Title'],getVideoUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands=cmd)

	pagination(soup,mSearchMv)
def allNgheSy():
	xbmc.executebuiltin('Container.SetViewMode(%d)'%(500))
	
	kw = getUserInput()
	url  = searchArtistUrl  + kw
	html = load(url)
	js = json.loads(html)
	if js['result']==True:
		artists = js['data'][0]['artist']
		for a in artists:
			aid = a['id']
			url = artistInfoApi.replace("_ID_",aid)
			ajs = json.loads(load(url))
			name = ajs['name']
			avatar = thumbBaseUrl + '/'+ ajs['avatar']
			href = homeUrl + ajs['link']
			addDir(name,href,mNgheSy,avatar,art=avatar)
	pass
def ngheSy(url):
	addDir(u'Bài hát',url +'/bai-hat',mNgheSySongs)
	addDir(u'Albums/Playlist',url +'/album',mNgheSyAlbum)
	addDir(u'Video',url +'/video',mNgheSyVideo)
	#addDir(u'Radio',url.replace('http://mp3.zing.vn/nghe-si','http://radio.zing.vn'),mNgheSyRadio)
	pass
def getNgheSySongs(soup):
	#html = load(url)
	#soup = BeautifulSoup(html)
	songs = []
	lis = soup.select('div.list-item li div.info-dp a')
	for a in lis:
		title = a['title']
		href=a['href']
		thumb='DefaultAudio.png'
		artist =''
		songs.append({'Title':title,'Artist':artist,'Link':href,'Thumb':thumb})
	return songs
def ngheSySongs(url):
	soup = BeautifulSoup(load(url))
	songs = getNgheSySongs(soup)
	cmd = createCommand('Play all',url,mPlayAllNgheSySongs)
	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = cmd)

	pagination(soup,mNgheSySongs)
	pass
def playAllNgheSySongs(url):
	soup = BeautifulSoup(load(url))
	
	songs = getNgheSySongs(soup)
	playAllSong(songs)
def ngheSyAlbum(url):
	html = load(url)
	soup = BeautifulSoup(html)
	thumbs = soup.select('div.album-item a.thumb')
	for a in thumbs:
		title= a['title']
		href = a['href']
		thumb = a.select('img')[0]['src']
		addDir(title,href,mAlbum,thumb)
	pagination(soup,mNgheSyAlbum)
def getNgheSyVideos(soup):
	thumbs = soup.select('div.album-item')
	songs = []
	for a in thumbs:
		title = a.select('a.txt-primary')[0].get_text()
		artist = a.select('.title-sd-item a')[0].get_text()
		href = a.select('a.thumb')[0]['href']
		thumb = a.select('a.thumb img')[0]['src']
		songs.append({'Title':title,'Artist':artist,'Link':href,'Thumb':thumb})
	return songs
def ngheSyVideo(url):
	xbmc.executebuiltin('Container.SetViewMode(%d)'%(500))
	
	soup = BeautifulSoup(load(url))
	songs = getNgheSyVideos(soup)
	cmd = createCommand("Play all video",url,mPlayAllNgheSyVideo)
	for s in songs:
		addVideo(s['Title'],getVideoUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = cmd)

	pagination(soup,mNgheSyVideo)
	pass
def playAllNgheSyVideo(url):
	soup = BeautifulSoup(load(url))
	songs = getNgheSyVideos(soup)
	playAllVideo(songs)
def hot():
	addDir(u'Albums hot','',mHotAlbum)
	addDir(u'MV hot','',mHotMV)
	addDir(u'Nhạc việt Hot','',mHotViet)
	addDir(u'Nhạc việt mới','',mHotVietNew)
	addDir(u'Playlist chọn lọc','',mHotPlaylist)
def findHomeSection(t):
	t = t.lower()

	html = load(homeUrl)
	soup = BeautifulSoup(html)
	sections = soup.select('div.section')
	for section in sections:
		titleA =section.select('h2.title-section a')
		if len(titleA)==0:continue
		title = titleA[0]
		sectionTitle = title['title'].lower()
		print sectionTitle

		if sectionTitle ==t:
			return section
	return None
def hotAlbum():
	section = findHomeSection('album hot')
	albums = findHotSectionItems(section)
	for a in albums:
		addDir(a['Title'] + ' - '+ a['Artist'],a['Link'],mAlbum,a['Thumb'])
def songsFromLis(ul):
	lis = ul.select('li')
	songs = []
	for li in lis:
		a = li.select('h3.txt-primary a')[0]
		title = a.get_text()
		href = a['href']
		songs.append({'Title':title,'Artist':'','Link':href,'Thumb':''})
	return songs

def hotViet():
	html = load(homeUrl)
	soup = BeautifulSoup(html)
	section = soup.select('div.section')[2]
	songs = songsFromLis(section.select('ul')[0])

	cmd = createCommand('Play all songs','',mPlayAllHotViet)

	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = cmd)

def playAllHotViet():
	html = load(homeUrl)
	soup = BeautifulSoup(html)
	section = soup.select('div.section')[2]

	songs = songsFromLis(section.select('ul')[0])
	playAllSong(songs)

def hotVietNew():
	html = load(homeUrl)
	soup = BeautifulSoup(html)
	section = soup.select('div.section')[2]
	songs = songsFromLis(section.select('ul')[1])

	cmd = createCommand('Play all songs','',mPlayAllHotVietNew)

	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = cmd)

def playAllHotVietNew():
	html = load(homeUrl)
	soup = BeautifulSoup(html)
	section = soup.select('div.section')[2]
	songs = songsFromLis(section.select('ul')[1])
	playAllSong(songs)

def findHotSectionItems(section):
	items = section.select('div.album-item')
	result =[]
	for item in items:
		thumb = item.select('img')[0]['src']
		title = item.select('.title-item')[0].get_text()
		artist = item.select('.title-sd-item')[0].get_text()
		href = item.select('a')[0]['href']
		result.append({'Title':title,'Artist':artist,'Thumb':thumb,'Link':href})

	return result
def hotMV():
	section = findHomeSection('video hot')
	videos = findHotSectionItems(section)
	cmd = createCommand('Play all videos','',mPlayAllHotMV)
	for v in videos:
		addVideo(v['Title'],getVideoUrl(v['Link']),v['Thumb'],v['Artist'],v['Thumb'],commands=cmd)

def hotPlayList():
	html = load(homeUrl)
	soup = BeautifulSoup(html)
	section = soup.select('div.full-section')[1]
	albums = []
	items = section.select("a.thumb")
	for item in items:
		thumb = item.select('img')[0]['src']
		title = item['title']
		href = item['href']
		albums.append({'Title':title,'Thumb':thumb,'Link':href,'Artist':''})

	for a in albums:
		addDir(a['Title'],a['Link'],mAlbum,a['Thumb'])

def playAllhotMV():
	section = findHomeSection('video hot')
	videos = findHotSectionItems(section)
	playAllVideo(videos)

def top100():
	addDir(u'Top 100 Việt nam','http://mp3.zing.vn/top100/Nhac-Tre/IWZ9Z088.html',mTop100Sub)
	addDir(u'Top 100 Âu mỹ','http://mp3.zing.vn/top100/Pop/IWZ9Z097.html',mTop100Sub)
	addDir(u'Top 100 Châu á','http://mp3.zing.vn/top100/Han-Quoc/IWZ9Z08W.html',mTop100Sub)
	addDir(u'Top 100 Hòa tấu','http://mp3.zing.vn/top100/Classical/IWZ9Z0BI.html',mTop100Sub)

def top100Sub(url):
	html = load(url)
	soup = BeautifulSoup(html)
	section = soup.select('div.section')[0]
	lis= section.select('.tab-menu li a')
	for a in lis:
		title = a.get_text()
		href = a['href']
		addDir(title,href,mTop100Song)

def getTop100Song(url):
	sid = getSongId(url)
	
	url = topApi + sid;
	text = load(url)
	j = json.loads(text)
	songs = []
	for s in j['data']:
		title = s['name']
		artist = s['artist']
		thumb = thumbBaseUrl + s['thumb']
		link = homeUrl + s['link']
		order  =s['order']
		title = '[%s] %s - %s'%(order,title,artist)
		songs.append({'Title':title,'Artist':'','Thumb':thumb,'Link':link})
	return songs;

	#html = load(url)
	#soup = BeautifulSoup(html)
	#items = soup.select('div.e-item')
	#songs = []
	#pos = 1
	#for item in items:
	#	a = item.select('a.thumb')[0]
	#	title =str(pos) +' - ' + a['title']
	#	href = a['href']
	#	thumb = a.img['src']
	#	pos = pos +1
	#	artist = item.select('div.fn-artist_list ')[0].get_text()
	#	songs.append({'Title':title,'Link':href,'Thumb':thumb,'Artist':artist})
	#return songs

def top100Song(url):
	songs  = getTop100Song(url)

	cmd = createCommand('Play all songs',url,mPlayAllTop100Song)
	for s in songs:
		addSong(s['Title'],getSongUrl(s['Link']),s['Thumb'],s['Artist'],s['Thumb'],commands = cmd)

def playAllTop100Song(url):
	songs  = getTop100Song(url)
	playAllSong(songs)

sysarg=str(sys.argv[1])
addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'videos')

params=get_params()
mode = mHome
url =''
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        mode=int(urllib.unquote_plus(params["mode"]))
except:	
        pass
if mode==None or mode == mHome:
	home()
elif mode == mAllChuDe:
	allChuDe(url)
elif mode==mChuDe:
	chuDe(url)
elif mode == mAlbum:
	album(url)
elif mode == mPlaySong:
	playSong(params)
elif mode == mPlayAllAlbum:
	playAllAlbum(url)
elif mode == mAllAlbum:
	allAlbum(url)
elif mode == mAlbumChuDe:
	albumChuDe(url)
elif mode == mAllVideo:
	allVideo(url)
elif mode == mVideoChuDe:
	videoChuDe(url)
elif mode == mPlayAllVideoChuDe:
	playAllVideoChuDe(url)
elif mode == mAllBxh:
	allBxh()
elif mode == mBxhSong:
	bxhSong(url)
elif mode==mPlayAllBxhSong:
	playAllBxhSong(url)
elif mode == mBxhAlbum:
	bxhAlbum(url)
elif mode == mBxhMv:
	bxhMv(url)
elif mode == mPlayAllBxhMv:
	playAllBxhMv(url)
elif mode == mSearch:
	search()
elif mode == mSearchSong:
	searchSong(url)
elif mode == mPlayAllSearchSong:
	playAllSearchSong(url)
elif mode == mAllNgheSy:
	allNgheSy()
elif mode == mNgheSy:
	ngheSy(url)
elif mode == mNgheSySongs:
	ngheSySongs(url)
elif mode == mPlayAllNgheSySongs:
	playAllNgheSySongs(url)
elif mode == mNgheSyAlbum:
	ngheSyAlbum(url)
elif mode == mNgheSyVideo:
	ngheSyVideo(url)
elif mode == mPlayAllNgheSyVideo:
	playAllNgheSyVideo(url)
elif mode == mSearchMv:
	searchMv(url)
elif mode == mPlayAllSearchVideo:
	playAllSearchVideo(url)
elif mode == mSearchAlbum:
	searchAlbum(url)
elif mode == mHot:
	hot()
elif mode ==mHotAlbum:
	hotAlbum()
elif mode == mHotMV:
	hotMV()
elif mode == mPlayAllHotMV:
	playAllhotMV()
elif mode == mHotViet:
	hotViet()
elif mode == mHotVietNew:
	hotVietNew()
elif mode == mPlayAllHotViet:
	playAllHotViet()
elif mode == mPlayAllHotVietNew:
	playAllHotVietNew()
elif mode == mHotPlaylist:
	hotPlayList()
elif mode == mAllTop100:
	top100()
elif mode == mTop100Sub:
	top100Sub(url)
elif mode == mTop100Song:
	top100Song(url)
elif mode == mPlayAllTop100Song:
	playAllTop100Song(url)

if mode <mPlaySong:
	xbmcplugin.endOfDirectory(int(sysarg))

