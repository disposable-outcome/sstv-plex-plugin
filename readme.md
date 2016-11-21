# Plex Plugin for SmoothStreamsTV

## About
This is a Plex plugin to access your SmoothStreamsTV account.

## Installation

- Unzip the downloaded file and place the smoothstreams2.bundle folder in the correct location for your Plex Media Server platform – see here for details: https://support.plex.tv/hc/en-us/articles/201106098-How-do-Ifind-the-Plug-Ins-folder-
- Using a web browser open Plex Web (http://PLEXSEVERIP:32400/web/index.html) and select Channels
- Smoothstreams should be in the Channels list now. Hover over the Smoothstreams channel and click on the cog to configure.
- You should then be able to open the Smoothstreams channel and start watching the streams

## Options
Set your username, password and service according to your provider.

### My Search
This is an area where you can setup custom entries for the plugin's home page. This will do a search based on the terms. You can use any strings to match the title, descrition or category in the guide. Items are seperate by a semicolon (;) so that you can make multiple entries.

You can also use the following keywords:

- NOW: Only return content that is currently on
- NEXT: Only return content that is starting in the next 90 minutes (can't be used at the same time as NOW)
- HD: Only return content that is 720p or better

#### Example
```
LiveNHL:NHL NOW HD;NFL;Movies NEXT HD;NOW HD;US Sports:NFL NHL NBA Baseball
```

Would make five entries.

- All shows in the NHL category and any other shows with the term 'NHL' in the title or description only in HD. This will get a custom title of 'LiveNHL'
- All shows in the NFL category and shows with the term 'NFL' in the title or description
- All shows in the Movies category that are HD that start in the next 90 minutes
- All shows that are currently on and are in HD
- All shows matching the words: NFL NHL NBA and Baseball with a custom title of 'US Sports'

### HD Only?
Only show content that is 720p or better in all menus.

### Sports Only?
- On: Use the default, official guide which only shows live sporting events.
- Off: Use the extended guide (thanks fog) which shows content for all channels. This will make the plugin slower because of the larger guide information.

## Updates
Download the latest release here: https://bitbucket.org/stankness/sstv-plex-plugin/get/master.zip

## Uninstall
- Delete the smoothstreams2.bundle folder from your plugins folder location - https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-thePlug-Ins-folder-
- Delete com.plexapp.plugins.smoothstreams2 - use this link to find the location depending on platform- https://support.plex.tv/hc/enus/articles/202967376-Clearing-Plugin-Channel-Agent-HTTP-Caches
- Delete com.plexapp.plugins.smoothstreams2 from the Data folder. Use the above link and change Caches for Data on the end of the string to find the location. Change %LOCALAPPDATA%\Plex Media Server\Plug-in Support\Caches\ to %LOCALAPPDATA%\Plex Media Server\Plug-in Support\Data

## Issues
Report issues here: https://bitbucket.org/stankness/sstv-plex-plugin/issues
