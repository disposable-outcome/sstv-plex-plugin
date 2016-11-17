# -*- coding: utf-8 -*-
###################################################################################################
#
#	Smoothstreams plugin for XBMC
#	Copyright (C) 2016 Smoothstreams
#
###################################################################################################
import sys
import os
import dateutil.parser
import datetime
import urllib2
import SmoothUtils
import SmoothAuth
import traceback
import operator
import bisect
import time
import calendar

Smoothstreams_URL = 'http://www.Smoothstreams.com'
Smoothstreams_URL1 = 'http://a.video.Smoothstreams.com/'
BASE_URL = 'http://www.Smoothstreams.com/videos'

MIN_CHAN = 1 # probably a given
MAX_CHAN = 120 # changed this to a preference 


VIDEO_PREFIX = ''
PREFIX = '/video/Smoothstreamsvideos'
CHANNELS = {'01': 'Channel 01', '02':'Channel 02'}
ORDERED_CHANNELS = ['01', '02']

NAME = 'Smoothstreams2'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
####################################################################################################

def Start():
	Log.Info("***SmoothStreams starting Python Version {0} TimeZone {1}".format(sys.version, time.timezone))
	loginResult = SmoothAuth.login()
	scheduleResult = SmoothUtils.GetScheduleJson()
	if Dict['SPassW'] is None:
		Log.Info('Bad login here, need to display it')
		ObjectContainer.title1 = NAME + " - Enter Login Details ->"
		ObjectContainer.art = R(ART)
	else:
		ObjectContainer.title1 = NAME
		ObjectContainer.art = R(ART)
		DirectoryObject.thumb = R("Smoothstreams-network.png")
		HTTP.Headers['User-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'

###################################################################################################

@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	Log.Info("***SmoothStreams ValidatePrefs Python Version {0} TimeZone {1}".format(sys.version, time.timezone))
	# Do we need to reset the extentions?
	Log.Info('ValidatePrefs')
	loginResult = SmoothAuth.login()
	scheduleResult = SmoothUtils.GetScheduleJson()
	Log.Info(repr(loginResult))
	return loginResult

#################################################################################################
@handler(PREFIX, NAME, thumb = ICON, art = ART)
def VideoMainMenu():
	Log.Info('VideoMainMenu called: ')
	MAX_CHAN = int(Prefs['numChannels'])
	oc = ObjectContainer()

	if (Dict['currentGuide'] == "Sports" and Prefs['sportsOnly']) or (Dict['currentGuide'] == "All" and not Prefs['sportsOnly']):
		scheduleResult = SmoothUtils.GetScheduleJson()

	if Dict['SPassW'] is None or Prefs['serverLocation'] is None or Prefs['username'] is None or Prefs['service'] is None:
		Log.Info('No password yet')
		ObjectContainer.title1 = NAME + ' - Enter Login Details and Server Preferences then Refresh ->'
		oc.add(PrefsObject(title = "Preferences", thumb = R("icon-prefs.png")))
	else:
		ObjectContainer.title1 = NAME
		oc.add(DirectoryObject(key = Callback(LiveMenu), title = "Live", thumb = R("Channels.png"), summary = "Live"))
		oc.add(DirectoryObject(key = Callback(ChannelsMenu), title = "Channels", thumb = R("Channels.png"), summary = "Channel List"))
		oc.add(DirectoryObject(key = Callback(CategoriesMenu), title = "Category", thumb = R("Category.png"), summary = "Category List"))
		oc.add(DirectoryObject(key = Callback(ScheduleListMenu), title = "Schedule", thumb = R("Schedule.png"), summary = "Schedule List"))

		# TODO: add custom categories
		#for category in sorted(categoryDict):
		if not Prefs['mySearch'] is None and len(Prefs['mySearch']) > 2:
			for mySearch in Prefs['mySearch'].split(";"):
				oc.add(DirectoryObject(key = Callback(SearchShows, query = mySearch), title = mySearch, thumb = SmoothUtils.GetDirectoryThumb(mySearch.replace(" NOW", "").replace(" HD", ""))))

		oc.add(InputDirectoryObject(key = Callback(SearchShows), title = "Search Shows", prompt = 'Enter show title'))

		# Preferences
		oc.add(PrefsObject(title = "Preferences", thumb = R("icon-prefs.png")))
			
	return oc
###################################################################################################

@route(PREFIX + '/searchShows')
def SearchShows(query):
	channelsDict = Dict['channelsDict']
	showsListAll = Dict['showsList']
	oc = ObjectContainer(title2 = "Search Results for {0}".format(query))
	for i in range(1, 5):
		Log.Info('sleeping 500ms for async schedule details to return')
		Thread.Sleep(0.5)
		if not channelsDict is None and not showsListAll is None:
			break
		#channelsDict = Dict['channelsDict']
		#showsListAll = Dict['showsList']

	currentTime = SmoothUtils.getCurrentTimeNative()
	summaryText = ''

	query = [x.strip().upper() for x in query.split(" ")]
	hdOnly = Prefs['hdOnly'] or "HD" in query
	nowOnly = "NOW" in query
	if hdOnly: query.remove("HD")
	if nowOnly: query.remove("NOW")

	showsList = []
	for show in showsListAll:
		keepShow = False
		showName = show['name'].upper()
		showCat = show['category'].upper()
		showDesc = show['description'].upper()
		if SmoothUtils.GetDateTimeNative(show['end_time']) >= currentTime and (not nowOnly or SmoothUtils.GetDateTimeNative(show['time']) <= currentTime):
			if not hdOnly or show['quality'].lower() == '720p' or show['quality'].lower() == '1080i':
				if len(query) == 0:
					keepShow = True
				else:
					for searchString in query:
						if showCat == searchString or showName.find(searchString) > -1 or showDesc.find(searchString) > -1:
							keepShow = True
							break
		if keepShow:
			showsList += [show]

	#for searchString in query:
	#	showsList += [i for i in showsListAll if SmoothUtils.GetDateTimeNative(i['end_time']) >= currentTime and (not nowOnly or SmoothUtils.GetDateTimeNative(i['time']) <= currentTime) and (i['name'].upper().find(searchString) > -1 or i['description'].upper().find(searchString) > -1) and (not hdOnly or i['quality'].lower() == '720p' or i['quality'].lower() == '1080i')]
	showsList.sort(key = lambda x: (x['time'], x['name'], x['quality']))

	showCount = 0
	for show in showsList:
		#Log.Info('searchShow result: %s' % show)

		channelNum = str(show['channel'])
		channelItem = channelsDict[channelNum]
		titleText = formatShowText(channelItem, show, currentTime, "{when} {title} {qual} {lang} {time} ({cat}) {chname} #{ch}")
		thumbText = '%02d'%int(channelNum)

		channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)

		if Prefs['channelDetails']:
			oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = channelNum), title = titleText, thumb = SmoothUtils.GetDirectoryThumb(text = thumbText)))
		elif SmoothUtils.GetDateTimeNative(show['time']) < currentTime:
			oc.add(VideoClipObject(
				key = Callback(CreateVideoClipObject, url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), title = titleText, thumb = SmoothUtils.GetVideoThumb(text = thumbText), container = True),
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
				title = SmoothUtils.fix_text(titleText),
				thumb = SmoothUtils.GetDirectoryThumb(text = thumbText),
				summary = SmoothUtils.fix_text(show['description']),
				items = [
					MediaObject(
						parts = [ PartObject(key = HTTPLiveStreamURL(url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), duration = 1000) ],
						optimized_for_streaming = True
					)
				]
				))
		else:
			oc.add(CreateVideoClipObject(
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum) + "&" + show['id'] + "&tm=" + str(show['time']).replace(" ", ""),
				title = SmoothUtils.fix_text(titleText),
				thumb = SmoothUtils.GetDirectoryThumb(text = thumbText)
			))

		showCount += 1
		if showCount == 100:
			break

	return oc

###################################################################################################
@route(PREFIX + '/channels')
def ChannelsMenu(url = None):
	oc = ObjectContainer(title2 = "Channels")
	Log.Info('ChannelsMenu')
	channelsDict = Dict['channelsDict']
	channelText = ''
	currentTime = SmoothUtils.getCurrentTimeNative()

	for i in range(1, 5):
		Log.Info('sleeping 500ms for async schedule details to return')
		Thread.Sleep(0.5)
		if not channelsDict is None:
			break
		channelsDict = Dict['channelsDict']
		categoryDict = Dict['categoryDict']
	
	for channelNum in range(1, MAX_CHAN + 1):
		if not channelsDict is None and str(channelNum) in channelsDict:
			channelItem = channelsDict[str(channelNum)]
			#channel = channelItem.name # get channel title
			nowPlaying = channelItem.NowPlaying()
			upcoming = channelItem.Upcoming()
			if not upcoming is None and len(upcoming) > 0:
				upcoming = upcoming[0]
			
			thumbText = '%02d'%channelNum
			if nowPlaying is None:
				titleText = formatShowText(channelItem, nowPlaying, currentTime, "#{ch} {chname}")
			else:
				titleText = formatShowText(channelItem, nowPlaying, currentTime, "#{ch} {chname} {title} {qual} {lang} {time} ({cat})")
			if not upcoming is None and len(upcoming) > 0:
				summaryText = formatShowText(channelItem, upcoming, currentTime, "{when} {title} {qual} {lang} {time} ({cat})")
			
			if Prefs['channelDetails']:
				channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)
				oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = channelNum), title = SmoothUtils.fix_text(titleText), thumb = SmoothUtils.GetDirectoryThumb(text = thumbText)))
			else:
				oc.add(VideoClipObject(
					key = Callback(CreateVideoClipObject, url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), title = SmoothUtils.fix_text(titleText), thumb = SmoothUtils.GetVideoThumb(text = thumbText), container = True),
					url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
					title = SmoothUtils.fix_text(titleText),
					thumb = SmoothUtils.GetVideoThumb(text = thumbText),
					summary = SmoothUtils.fix_text(summaryText),
					items = [
						MediaObject(
							parts = [ PartObject(key = HTTPLiveStreamURL(url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), duration = 1000) ],
							optimized_for_streaming = True
						)
					]
					))
	return oc
###################################################################################################
@route(PREFIX + '/live')
def LiveMenu(url = None):
	oc = ObjectContainer(title2 = "Live")
	Log.Info('LiveMenu')
	channelsDict = Dict['channelsDict']
	nowPlayingDict = Dict['nowPlayingDict']
	currentTime = SmoothUtils.getCurrentTimeNative()

	for i in range(1, 5):
		Log.Info('sleeping 500ms for async schedule details to return')
		Thread.Sleep(0.5)
		if not channelsDict is None and not nowPlayingDict is None:
			break
		channelsDict = Dict['channelsDict']
		nowPlayingDict = Dict['nowPlayingDict']
	
	showsList = [i for i in nowPlayingDict if SmoothUtils.GetDateTimeNative(i['end_time']) >= currentTime and (not Prefs['hdOnly'] or i['quality'].lower() == '720p' or i['quality'].lower() == '1080i')]
	showsList.sort(key = lambda x: (x['category'], x['name'], x['quality'], x['time']))

	for i in range(0, len(showsList)):
		show = showsList[i]
		showName = None
		channelNum = str(show['channel'])
		if show['category'].lower().replace(" ", "") in ["", "tv", "generaltv"]:
			thumbText = '%02d'%int(channelNum)
			show['category'] = ""
		else:
			thumbText = show['category']
		channelItem = channelsDict[str(channelNum)]
		channelText2 = channelItem.GetStatusText2()

		titleText = formatShowText(channelItem, show, currentTime, "{cat} {title} {qual} {lang} {time} {chname} #{ch}")

		artUrl = 'http://smoothstreams.tv/schedule/includes/images/uploads/8ce52ab224906731eaed8497eb1e8cb4.png'
		channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)

		if Prefs['channelDetails']:
			oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = channelNum), title = titleText, thumb = SmoothUtils.GetDirectoryThumb(text = thumbText)))
		else:
			oc.add(VideoClipObject(
				key = Callback(CreateVideoClipObject, url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), title = titleText, thumb = SmoothUtils.GetVideoThumb(text = channelText2), container = True),
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
				title = SmoothUtils.fix_text(titleText),
				thumb = SmoothUtils.GetDirectoryThumb(text = thumbText),
				summary = SmoothUtils.fix_text(show['description']),
				items = [
					MediaObject(
						parts = [ PartObject(key = HTTPLiveStreamURL(url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), duration = 1000) ],
						optimized_for_streaming = True
					)
				]
				))

	return oc
#################################################################################################
@route(PREFIX + '/categories')
def CategoriesMenu():
	Log.Info("CategoriesMenu")
	oc = ObjectContainer(title2 = "Categories")
	Log.Info('Categories')
	channelsDict = Dict['channelsDict']
	categoryDict = Dict['categoryDict']
	channelText = ''
	
	for i in range(1, 5):
		if not channelsDict is None and not categoryDict is None:
			break
		Log.Info('sleeping 500ms for async schedule details to return')
		Thread.Sleep(0.5)
		channelsDict = Dict['channelsDict']
		categoryDict = Dict['categoryDict']

	for category in sorted(categoryDict):
		oc.add(DirectoryObject(key = Callback(CategoryMenu, url = category), title = category, thumb = SmoothUtils.GetDirectoryThumb(category)))
	
	return oc
#################################################################################################
@route(PREFIX + '/category')
def CategoryMenu(url = None):
	Log.Info("CategoryMenu " + url)
	if url is None:
		oc = ObjectContainer(title2 = "Category")
	else:
		oc = ObjectContainer(title2 = url)
	channelsDict = Dict['channelsDict']
	categoryDict = Dict['categoryDict']
	channelText = ''
	currentTime = SmoothUtils.getCurrentTimeNative()

	for i in range(1, 5):
		Log.Info('sleeping 500ms for async schedule details to return')
		Thread.Sleep(0.5)
		if not channelsDict is None and not channelsDict is None:
			break
		channelsDict = Dict['channelsDict']
		categoryDict = Dict['categoryDict']
	
	# filter and sort the shows for the category by start time
	showsList = sorted([i for i in categoryDict[url] if SmoothUtils.GetDateTimeNative(i['end_time']) >= currentTime and (not Prefs['hdOnly'] or i['quality'].lower() == '720p' or i['quality'].lower() == '1080i')], key = lambda x: (x['time'], x['name'], x['quality']))

	showCount = 0
	for show in showsList:
		Log.Info('SHOW: %s' % show)
		showCount += 1
		showName = None
		channelNum = str(show['channel'])
		thumbText = '%02d'%int(channelNum)
		channelItem = channelsDict[str(channelNum)]
		titleText = formatShowText(channelItem, show, currentTime, "{when} {title} {qual} {lang} {time} {chname} #{ch}")
		Log.Info("TITLE: " + titleText)

		artUrl = 'http://smoothstreams.tv/schedule/includes/images/uploads/8ce52ab224906731eaed8497eb1e8cb4.png'
		channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)

		if Prefs['channelDetails']:
			oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = channelNum), title = titleText, summary = SmoothUtils.fix_text(show['description']), thumb = SmoothUtils.GetDirectoryThumb(text = thumbText)))
		elif SmoothUtils.GetDateTimeNative(show['time']) < currentTime:
			oc.add(VideoClipObject(
				key = Callback(CreateVideoClipObject, url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), title = titleText, thumb = SmoothUtils.GetVideoThumb(text = thumbText), container = True),
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
				title = SmoothUtils.fix_text(titleText),
				summary = SmoothUtils.fix_text(show['description']),
				thumb = SmoothUtils.GetDirectoryThumb(text = thumbText),
				items = [
					MediaObject(
						parts = [ PartObject(key = HTTPLiveStreamURL(url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), duration = 1000) ],
						optimized_for_streaming = True
					)
				]
				))
		else:
			oc.add(CreateVideoClipObject(
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum) + "&" + show['id'] + "&tm=" + str(show['time']).replace(" ", ""),
				title = SmoothUtils.fix_text(titleText),
				summary = SmoothUtils.fix_text(show['description']),
				thumb = SmoothUtils.GetDirectoryThumb(text = thumbText)
			))

		if showCount == 100:
			Log.Info('MAX SHOWS REACHED')
			break

	return oc
###################################################################################################
@route(PREFIX + '/channels/schedulelist')
def ScheduleListMenu(startIndex = 0):
	pageCount = int(Prefs['pageCount'])
	endIndex = int(startIndex) + pageCount

	oc = ObjectContainer(title2 = "Schedule List")
	Log.Info('ScheduleListMenu %s %s %s' % (startIndex, endIndex, pageCount))
	channelsDict = Dict['channelsDict']
	showsList = Dict['showsList']
	channelText = ''
	
	for i in range(1, 5):
		Log.Info('sleeping 500ms for async schedule details to return')
		Thread.Sleep(0.5)
		if not channelsDict is None and not showsList is None:
			break
		channelsDict = Dict['channelsDict']
		showsList = Dict['showsList']

	parser = dateutil.parser()
	currentTime = SmoothUtils.getCurrentTimeNative()

	showsList = [i for i in showsList if SmoothUtils.GetDateTimeNative(i['end_time']) >= currentTime and (not Prefs['hdOnly'] or i['quality'].lower() == '720p' or i['quality'].lower() == '1080i')]
	showsList.sort(key = lambda x: (x['time'], x['name'], x['quality']))
	#Log.Debug('showsListLen %s' % len(showsList))

	if endIndex > len(showsList):
		endIndex = len(showsList)
	
	for i in range(int(startIndex), int(endIndex)):
		show = showsList[i]
		channelSeparator = ' - '
		
		if SmoothUtils.GetDateTimeNative(show['end_time']) <= currentTime:
			channelSeparator = ' * '
		channelItem = None
		channelText = u''
		channelNum = str(show['channel'])
		channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)
		if SmoothUtils.GetDateTimeNative(show['time']) > currentTime:
			channelUrl += "&" + show['id']

		if show['category'].lower().replace(" ", "") in ["", "tv", "generaltv"]:
			thumbFile = SmoothUtils.GetVideoThumb(text = '%02d' % int(channelNum))
			show['category'] = ""
		else:
			thumbFile = SmoothUtils.GetDirectoryThumb(text = show['category'])

		if not channelsDict is None and not channelsDict[channelNum] is None:
			channelItem = channelsDict[channelNum]
			channelText = channelItem.GetStatusText()
			channelText = formatShowText(channelItem, show, currentTime, "{when} {time} #{ch} {chname} {title} {qual} {lang} ({cat})")
		else:
			channelText = '%02d {0} ' % (channelNum, channelSeparator)
			channelText = formatShowText(channelItem, show, currentTime, "")

		# CHECK PREFS for Scheduled Channel Details 
		if Prefs['channelDetails']:
		 	oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = channelNum), title = SmoothUtils.fix_text(channelText), summary = SmoothUtils.fix_text(show['description']), thumb = thumbFile))
		else:
			oc.add(VideoClipObject(
				key = Callback(CreateVideoClipObject, url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), title = SmoothUtils.fix_text(channelText), thumb = thumbFile, container = True),
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
				title = SmoothUtils.fix_text(channelText),
				summary = SmoothUtils.fix_text(show['description']),
				thumb = thumbFile,
				items = [
					MediaObject(
						parts = [ PartObject(key = HTTPLiveStreamURL(url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), duration = 1000) ],
						optimized_for_streaming = True
					)
				]
			))

	Log.Info('endInd %s'.format(endIndex))
	endIndex = int(endIndex)
	Log.Info(' vs %s'.format(len(showsList)))

	if int(endIndex) < len(showsList):
		Log.Info('adding next button')
		oc.add(NextPageObject(key = Callback(ScheduleListMenu, startIndex = int(endIndex)), title = "Next Page", thumb = 'more.png'))
	return oc
#################################################################################################
@route(PREFIX + '/channels/playmenu')
def PlayMenu(url = None,channelNum = None):
	### This is the detailed PLAY menu after a channel has been selected which shows NOW PLAYING, and then the shows that will be on later
	Log.Info('PlayMenu with Url ' + url)
	oc = ObjectContainer(title1 = 'Channel ' + channelNum)
	title = channelNum
	addedItems = False
	channelsDict = Dict['channelsDict']
	if not channelsDict is None and not channelsDict[str(channelNum)] is None:
		channel = channelsDict[str(channelNum)]
		title = channel.name
		upcomingShows = channel.Upcoming()
		oc.title1 = title
		channelItem = channelsDict[str(channelNum)]
		channelText = SmoothUtils.fix_text(channelItem.GetStatusText())
		channelText1 = SmoothUtils.fix_text(channelItem.GetStatusText1())
		channelText2 = SmoothUtils.fix_text(channelItem.GetStatusText2())
		channelText3 = SmoothUtils.fix_text(channelItem.GetStatusText3())
		if not upcomingShows is None and len(upcomingShows) > 0:
			nowPlaying = channel.NowPlaying()
			if nowPlaying is None:
					oc.add(VideoClipObject(
					key = Callback(CreateVideoClipObject, url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), title = SmoothUtils.fix_text(channelText), thumb = R(channelText2 + '.png'), container = True),
					url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
					title = SmoothUtils.fix_text(channelText1),
					thumb = R(channelText2 + '.png'),
					items = [
						MediaObject(
							parts = [ PartObject( key = HTTPLiveStreamURL(url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum)), duration = 1000) ],
							optimized_for_streaming = True
						)
					]
					))
			else:
				# we only get here if we couldn't get any schedule info
				oc.add(CreateVideoClipObject(
					url = HTTPLiveStreamURL(SmoothUtils.GetFullUrlFromChannelNumber(channelNum)),
					title = SmoothUtils.fix_text((nowPlaying['name'] + ' (' + nowPlaying['quality'] + ') ' + SmoothUtils.GetShowTimeText(nowPlaying))),
					thumb = R(channelText2 + '.png')
				))
			for show in upcomingShows:
				oc.add(CreateVideoClipObject(
					url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum) + "&" + show['id'],
					title = SmoothUtils.fix_text(('LATER: ' + show['name'] + ' (' + show['quality'] + ') ' + SmoothUtils.GetShowTimeText(show))),
					thumb = R(channelText2 + '.png')
				))

			addedItems = True
	
	if not addedItems:
		oc.title1 = title
		oc.add(CreateVideoClipObject(
				url = SmoothUtils.GetFullUrlFromChannelNumber(channelNum),
				title = SmoothUtils.fix_text(('WATCH: ' + title).encode("iso-8859-1")),
				thumb = None
			))
	try:
		# add browse options for Next/Prev channel
		prevChan = int(channelNum) - 1
		if prevChan < MIN_CHAN:
			prevChan = MAX_CHAN
		channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(prevChan)
		oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = prevChan), title = ('/\\ ' + channelsDict[str(prevChan)].GetStatusText()).encode("iso-8859-1")))

		nextChan = int(channelNum) + 1
		if nextChan > MAX_CHAN:
			nextChan = MIN_CHAN
		channelUrl = SmoothUtils.GetFullUrlFromChannelNumber(nextChan)
		oc.add(DirectoryObject(key = Callback(PlayMenu, url = channelUrl, channelNum = nextChan), title = ('\\/ ' + channelsDict[str(nextChan)].GetStatusText()), thumb = R(channelText2 + '.png')))
	except Exception, e:
		Log.Error('Could not add next/prev chan browse options')
		Log.Error(str(e))
		Log.Error(traceback.print_exc())

	return oc
###############################################################################################

#####https://github.com/Cigaras/IPTV.bundle/blob/master/Contents/Code/__init__.py
@route(PREFIX + '/listitems', items_dict = dict)
def ListItems(items_dict, group):
	oc = ObjectContainer(title1 = L(group))
	items_list = []
	for i in items_dict:
		if items_dict[i]['group'] == group or group == 'All':
			items_list.append(items_dict[i])
	for item in items_list:
		# Simply adding VideoClipObject does not work on some clients (like LG SmartTV),
		# so there is an endless recursion - function CreateVideoClipObject calling itself -
		# and I have no idea why and how it works...
		oc.add(CreateVideoClipObject(
			url = item['url'],
			title = item['title'],
			thumb = item['thumb']
		))
	return oc

@route(PREFIX + '/createvideoclipobject')
def CreateVideoClipObject(url, title, thumb = None, container = False, art = ART, **kwargs):
	vco = VideoClipObject(
		key = Callback(CreateVideoClipObject, url = url, title = SmoothUtils.fix_text(title), thumb = thumb, art = ART, container = True),
		#rating_key = url,
		url = url,
		title = SmoothUtils.fix_text(title),
		thumb = thumb,
		items = [
			MediaObject(
				#container = Container.MP4,		# MP4, MKV, MOV, AVI
				#video_codec = VideoCodec.H264,	# H264
				#audio_codec = AudioCodec.AAC,	# ACC, MP3
				#audio_channels = 2,			# 2, 6
				parts = [ PartObject(key = GetVideoURL(url = url), duration = 1000) ],
				optimized_for_streaming = True
			)
		]
	)

	if container:
		return ObjectContainer(objects = [vco])
	else:
		return vco
	return vco

def GetVideoURL(url, live = True):
	if url.startswith('rtmp') and False:
		Log.Debug('*' * 80)
		Log.Debug('* url before processing: %s' % url)
		Log.Debug('* url after processing: %s' % RTMPVideoURL(url = url, live = live))
		Log.Debug('*' * 80)
		return RTMPVideoURL(url = url, live = live)
	elif url.startswith('mms') and False:
		return WindowsMediaVideoURL(url = url)
	else:
		return HTTPLiveStreamURL(url = url)

def GetThumb(thumb):
	if thumb and thumb.startswith('http'):
		return thumb
	elif thumb and thumb <> '':
		Log.Info('thumb for ' + thumb)
		return R(thumb)
	else:
		return None

def GetAttribute(text, attribute, delimiter1 = '="', delimiter2 = '"'):
	x = text.find(attribute)
	if x > -1:
		y = text.find(delimiter1, x + len(attribute)) + len(delimiter1)
		z = text.find(delimiter2, y)
		if z == -1:
			z = len(text)
		return unicode(text[y:z].strip())
	else:
		return ''

def getShowText(show, currentTime):
	language = ""
	if "language" in show and show['language'].upper() != "US":
		language = ' ' + show['language'].upper()

	showText = "Ch" + show['channel'] + " " + show['name'] + " " + show['quality'] + language + " " + SmoothUtils.GetShowTimeText(show)
	if SmoothUtils.GetDateTimeNative(show['time']) > currentTime:
		return "LATER: " + showText
	else:
		return "LIVE: " + showText

def formatShowText(channel, show, currentTime, formatString):
	language = ""
	
	if " - " in channel.name:
		chanName = channel.name.split(" - ")[1]
	else:
		chanName = channel.name

	if show is None:
		retVal = formatString.replace("{ch}", channel.channel_id).replace("{chname}", chanName)
	else:
		if "language" in show and show['language'].upper() != "US":
			language = show['language'].upper()

		if "720p" in chanName.lower():
			chanName = chanName.replace(" 720P", "HD")
		
		showTime = SmoothUtils.GetDateTimeNative(show['time'])
		if showTime > currentTime:
			if showTime.date() == currentTime.date():
				when = "LATER"
			elif (showTime - datetime.timedelta(days=1)).date() == currentTime.date():
				when = "TOM"
			else:
				when = calendar.day_name[showTime.weekday()][:3].upper()
		else:
			when = ""

		if "category" in show and show["name"].startswith(show["category"] + ":") and show["category"] != "News":
			show["name"] = show["name"].replace(show["category"] + ":", "").strip()

		retVal = formatString.replace("{ch}", channel.channel_id).replace("{chname}", chanName).replace("{title}", show['name']).replace("{qual}", show["quality"].replace("hqlq", "")).replace("{time}", SmoothUtils.GetShowTimeText(show)).replace("{lang}", language).replace("{when}", when).replace("{cat}", show['category'])
	
	return retVal.replace("()", "").replace("  ", " ").strip()

###################################################################################################
# Notes about xpaths
# .// means any child/grandchild of the currently selected node, rather than anywhere in the document. Particularly important when dealing with loops.
# // = any child or grand-child ( you can use // so that you don't have to specify all the parents before it). Be careful to be specific enough to avoid confusion.
# / = direct child of the parent (for example of the entire page)