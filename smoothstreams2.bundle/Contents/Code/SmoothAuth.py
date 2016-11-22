# -*- coding: utf-8 -*-
###################################################################################################
#
#   Smoothstreams plugin for XBMC
#   Copyright (C) 2016 Smoothstreams
#
###################################################################################################
import time
import calendar
import dateutil.parser
import datetime
import urllib
import re
import SmoothUtils
from dateutil.tz import tzlocal

LOGIN_TIMEOUT_MINUTES = 60

def login():
	if not isLoggedIn():
		resetCredentials()
		if "service" in Prefs:
			service = Prefs["service"]
			Log.Info("calling streams login for service " + service)
			url = 'http://smoothstreams.tv/schedule/admin/dash_new/hash_api.php'
			if "username" in Prefs and "password" in Prefs:
				Log.Info("login url " + url + " for username " + Prefs['username'])
				uname = Prefs['username']
				pword = Prefs['password']
				if uname != '':
					post_data = {"username": uname, "password": pword, "site": getLoginSite()}
					result = JSON.ObjectFromURL(url, values = post_data, encoding = 'utf-8', cacheTime = LOGIN_TIMEOUT_MINUTES * 100)
					try:
						Log.Info(result)
						Dict["SUserN"] = result["code"]
						Dict["SPassW"] = result["hash"]
						Dict["validUntil"] = datetime.datetime.now() + datetime.timedelta(minutes = LOGIN_TIMEOUT_MINUTES)
						Dict.Save()
						Log.Info("Login complete")
						return True
					except Exception as e:
						Log.Error("Error parsing login result: " + repr(e) + " - " + repr(result))

					if "error" in result:
						Log.Error(result["error"])
					else:
						Log.Info('Got login info')
					Log.Error("Login failure: " + repr(result))
				return MessageContainer("Error", "Login failure for " + url)
			else:
				return MessageContainer("Error", "No login or password specified")
		else:
			return MessageContainer("Error", "No service selected")

def resetCredentials():
	Dict['SUserN'] = None
	Dict['SPassW'] = None
	Dict.Save()

def isLoggedIn():
	if Dict['validUntil'] is None:
		return False
	elif Dict['validUntil'] > datetime.datetime.now():
		return True
	else:
		return False

def getLoginSite():
	serviceName = Prefs['service'] 
	if serviceName =='MyStreams':
		return 'viewms'
		#return 'mystreams'
	elif serviceName == 'Live247':
		return 'view247'
		#return 'live247'
	elif serviceName == 'StarStreams':
		return 'viewss'
		#return 'starstreams'
	elif serviceName == 'StreamTVNow':
		return 'viewstvn'
	elif serviceName == 'MMA-TV/MyShout':
		return 'mma-tv'
	else:
		Log.Error('getLoginSite() called with invalid service name')
		return None
