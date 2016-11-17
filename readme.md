# Plex Plugin for SmoothStreamsTV

## About
This is a Plex plugin to access your SmoothStreamsTV account.

## Installation
Place the smoothstreams2.bundle folder in your Plex Media Server/plug-ins folder.

## Options
Set your username, password and service according to your provider.

### My Search
This is an area where you can setup custom entries for the plugin's home page. This will do a search based on the terms. You can use any strings to match the title, descrition or category in the guide. Items are seperate by a semicolon (;) so that you can make multiple entries.

You can also use the following keywords:

 - NOW: Only return content that is currently on
 - HD: Only return content that is 720p or better

#### Example
```
NHL NOW HD;NFL;Movies HD;NOW HD
```

Would make four entries.
    - All shows in the NHL category and any other shows with the term 'NHL' in the title or description only in HD
    - All shows in the NFL category and shows with the term 'NFL' in the title or description
    - All shows in the Movies category that are HD
    - All shows that are currently on and are in HD

### HD Only?
Only show content that is 720p or better in all menus.

### Sports Only?
 - On: Use the default, official guide which only shows live sporting events.
 - Off: Use the extended guide (thanks fog) which shows content for all channels. This will make the plugin slower because of the larger guide information.
