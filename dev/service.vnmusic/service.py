import time
import xbmc
import urlparse
import SimpleHTTPServer
import SocketServer
import urllib2
import urllib
import re
import json
import base64
import requests
import httplib


songInfoApi = 'http://api.mp3.zing.vn/api/mobile/song/getsonginfo?keycode=fafd463e2131914934b73310aa34a23f&requestdata={"id":"_ID_ENCODED_"}'
videoInfoApi ='http://api.mp3.zing.vn/api/mobile/video/getvideoinfo?keycode=fafd463e2131914934b73310aa34a23f&requestdata={"id":"_ID_ENCODED_"}'
zingTvApi ='http://api.tv.zing.vn/2.0/media/info?api_key=d04210a70026ad9323076716781c223f&session_key=91618dfec493ed7dc9d61ac088dff36b&&media_id='

def load(url):
	r = requests.get(url)
	return r.text
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
def getZTVSource(source,quality=3):
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
		return getZTVSource(source,quality-1)
def getZVideoSource(source,quality=4):
	log('getVideoSource:'+str(quality))

	result = None

	if quality <0 :
		return result

	ss = []
	if '240' in source:
		ss.append(source['240'])
	else:
		ss.append(None)

	if '360' in source:
		ss.append(source['360'])
	else:
		ss.append(None)

	if '480' in source:
		ss.append(source['480'])
	else:
		ss.append(None)

	if '720' in source:
		ss.append(source['720'])
	else:
		ss.append(None)

	if '1080' in source:
		ss.append(source['1080'])
	else:
		ss.append(None)
	
	#log('Source:%d - %s'%(quality,ss[quality]))

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
		return getZVideoSource(source,quality-1)

def getZAudioSource(source,audio_quality=2):
	log('getAudioSource:'+str(audio_quality))

	result = None
	if(audio_quality<0):
		return result

	ss = []
	if '128' in source:
		ss.append(source['128'])
	else:
		ss.append(None)

	if '320' in source:
		ss.append(source['320'])
	else:
		ss.append(None)

	if 'lossless' in source:
		ss.append(source['lossless'])
	else:
		ss.append(None)

	if ss[audio_quality]!=None:
		result = ss[audio_quality]
	else:
		for i in range(audio_quality,-1,-1):
			if ss[i] != None:
				result = ss[i]
		if result != None:
			for i in range(audio_quality,len(ss)):
				if ss[i] != None:
					result = ss[i]
					
	if result != None and checkUrl(result):
		return result
	else:
		return getZAudioSource(source,audio_quality-1)

def getMp3ZingSong(sid,q):
	url = songInfoApi.replace('_ID_ENCODED_',sid)
	js = json.loads(load(url))
	url = getZAudioSource(js['source'],q)
	return url
def getZingTVVideo(sid,q):
	url = zingTvApi + sid
	js = json.loads(load(url))
	url = getZTVSource(js['response']['other_url'],q)
	return url
def getMp3ZingVideo(sid,q):
	url = videoInfoApi.replace('_ID_ENCODED_',sid)
	js = json.loads(load(url))
	source = getZVideoSource(js['source'],q)
	return source
def getTalkTVVideo(sid):
	#loadPlayer.manifestUrl = "http://live.csmtalk.vcdn.vn/hls/6b1cc68ba8735185ada742e8713567c4/55f10fd0/elorenhat/index.m3u8";
	url = 'http://talktv.vn/'+sid
	html = load(url)
	lines = html.split('\n')
	for line in lines:
		line = line.strip()
		if 'loadPlayer.manifestUrl' in line:
			line = line.replace('loadPlayer.manifestUrl','').replace('"','').replace(';','').replace('=','').strip()
			return line
	return None
def log(m):
	sys.stdout.write(m)
	pass
class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

	def redirect(self,link):
		self.send_response(301)
		self.send_header('Content-type','text/html')
		self.send_header('Location', link)
		self.end_headers()
		#log('link:'+link)
		pass
	def do_HEAD(self):
		self.do_GET()

	def do_GET(self):
		q = urlparse.urlparse(self.path)
		queries = urlparse.parse_qs(q.query)
		
		self.log_request()

		if "mp3ZAudio?" in self.path:
			link = getMp3ZingSong(queries['sid'][0],int(queries['q'][0]))
			if link == None:
				log(queries['sid'][0]+' link not found')
				pass
			self.redirect(link)
		elif "mp3ZVideo?" in self.path:
			link = getMp3ZingVideo(queries['sid'][0],int(queries['q'][0]))
			self.redirect(link)
		elif 'ZingTV?' in self.path:
			link = getZingTVVideo(queries['sid'][0],int(queries['q'][0]))
			self.redirect(link)
		elif 'TalkTV?' in self.path:
			link = getTalkTVVideo(queries['sid'][0])
			self.redirect(link)
	def log_request(self, code='-', size='-'):
		sys.stdout.write("%s %s %s" % (self.requestline, str(code), str(size)))

if __name__ == '__main__':

	PORT = 9998
	handler = MyRequestHandler
	httpd = SocketServer.TCPServer(("", PORT), handler)
	sys.stdout.write("serving at port %d" % PORT)
	httpd.serve_forever()