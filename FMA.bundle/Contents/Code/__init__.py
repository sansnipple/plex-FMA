# Free Music Archive (http://freemusicarchive.org) plugin for plex media server

# copyright 2010 Billy Joe Poettgen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



import re, string
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *


FMA_PREFIX   = "/music/FMA"

API_ROOT = "http://freemusicarchive.org/api/get/"

CACHE_INTERVAL = 3600


###################################################################################################
def Start():
  Plugin.AddPrefixHandler(FMA_PREFIX, MainMenu, 'Free Music Archive', 'icon-default.png', 'art-default.png')
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.title1 = 'Free Music Archive'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.png')
  DirectoryItem.thumb=R('icon-default.png')
  InputDirectoryItem.thumb=R('icon-default.png')
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################


def MainMenu():
	dir = MediaContainer(viewGroup='List')

	return dir	

##################################################################################################



def Tracks(sender, search="", query="", sort="", sort_dir="", page="1"):
  dir = MediaContainer(viewGroup='List')
  url = API_ROOT + "tracks.xml" + "?" + search + "=" + query + "&limit=50" + "&page=" + page + "&sort_by=" + sort + "&sort_dir=" + sort_dir
  results = XML.ElementFromURL(url , errors="ignore")
  for i in range(len(results.xpath("//dataset/value"))):
    track = {}
    track[url]       = results.xpath("//dataset/value[%i]/track_url/text()" % (i+1))
    track[title]     = results.xpath("//dataset/value[%i]/track_title/text()" % (i+1))
    track[artist]    = results.xpath("//dataset/value[%i]/artist_name/text()" % (i+1))
    track[album]     = results.xpath("//dataset/value[%i]/album_title/text()" % (i+1))
    
  
    #gotta do the redirect thing here to grab the actual mp3 url
    dir.Append(Function(TrackItem(getTrack, title=track[title], artist=track[artist], album=track[album], contextKey=track), url=track[url]))
  return dir

def getTrack(sender, url=""):
  
  page  = XML.ElementFromURL(url, errors="ignroe")
  track = page.xpath("//a[@title='Download']/@href")
  
  return Redirect(realURL)