__author__ = 'MrOdin'
import re, os, sys, StringIO
import xbmc
import xbmcaddon,xbmcplugin,xbmcgui
from bs4 import BeautifulSoup

def addItems(items):
	for i, item in items:
		listItem = xbmcgui.ListItem(label=item["label"], label2=item["label2"], iconImage=item["icon"], thumbnailImage=item["thumbnail"])
		if item.get("info"):
				listItem.setInfo("video", item["info"])
		if item.get("stream_info"):
				for type_, values in item["stream_info"].items():
						listItem.addStreamInfo(type_, values)
		if item.get("art"):
				listItem.setArt(item["art"])
		if item.get("context_menu"):
				listItem.addContextMenuItems(item["context_menu"])
		listItem.setProperty("isPlayable", item["is_playable"] and "true" or "false")
		if item.get("properties"):
				for k, v in item["properties"].items():
						listItem.setProperty(k, v)
		listitems[i] = (item["path"], listItem, not item["is_playable"])

	xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
	xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)
