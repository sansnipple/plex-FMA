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



def Tracks(sender, search_by="", query="", sort_by="", sort_dir="", page="1"):
  dir = MediaContainer(viewGroup='List')
  url = API_ROOT + "tracks.xml?" + search_by + "=" + query + "&limit=50" + "&page=" + page + "&sort_by=" + sort_by + "&sort_dir=" + sort_dir
  results = XML.ElementFromURL(url , errors="ignore")
  for i in range(len(results.xpath("//dataset/value"))):
    track              = {}
    track[track_id]    = results.xpath("//dataset/value[%i]/track_id/text()" % (i+1))
    track[track_url]   = results.xpath("//dataset/value[%i]/track_url/text()" % (i+1))
    track[track_title] = results.xpath("//dataset/value[%i]/track_title/text()" % (i+1))
    track[artist_name] = results.xpath("//dataset/value[%i]/artist_name/text()" % (i+1))
    track[artist_id]   = results.xpath("//dataset/value[%i]/artist_id/text()" % (i+1))
    track[album_title] = results.xpath("//dataset/value[%i]/album_title/text()" % (i+1))
    track[album_id]    = results.xpath("//dataset/value[%i]/album_id/text()" % (i+1))
    # may need to de-listify these xpath results later, i'm not sure how they'll return
  
    #gotta do the redirect thing here to grab the actual mp3 url
    dir.Append(Function(TrackItem(getTrack, title=track[track_title], artist=track[artist_name], album=track[album_title], contextKey=track), url=track[track_url]))

  #pagination
  total_pages = int(results.xpath("/data/total_pages//text()"))
  if total_pages > 1:
     current_page = int(results.xpath("/data/page//text()"))
     if current_page < total_pages:
       dir.Append(Function(DirectoryItem(Tracks, title="Next Page"), search_by=search_by, query=query, sort_by=sort_by, sort_dir=sort_dir, page=str(current_page+1)))
  
  
  return dir

def getTrack(sender, url=""):
  
  page  = XML.ElementFromURL(url, errors="ignroe")
  track = page.xpath("//a[@title='Download']/@href")
  
  return Redirect(realURL)

def Albums(sender, artist_id="", genre_handle="", curator_handle="", page = "1",  sort_by="", sort_dir=""):
  dir = MediaContainer(viewGroup='List')
  url = API_ROOT + "albums.xml?" + "artist_id" + artist_id + "&genre_handle=" + genre_handle + "&curator_handle=" + curator_handle + "&limit=50" + "&page=" + page + "&sort_by=" + sort_by + "&sort_dir=" + sort_dir
  results = XML.ElementFromURL(url , errors="ignore")
  for i in range(len(results.xpath("//dataset/value"))):
    album                     = {}
    album[album_id]           = results.xpath("//dataset/value[%i]/album_id/text()" % (i+1))
    album[album_title]        = results.xpath("//dataset/value[%i]/album_title/text()" % (i+1))
    album[album_type]         = results.xpath("//dataset/value[%i]/album_type/text()" % (i+1))
    album[artist_name]        = results.xpath("//dataset/value[%i]/artist_name/text()" % (i+1))
    album[album_information]  = String.StripTags(results.xpath("//dataset/value[%i]/album_information/text()" % (i+1)))
    # I have no clue how well that StipTags  will work to clean up album_information, that field is quite a mess, may have to remove if its failing loudly
    
    dir.Append(Function(DirectoryItem(Tracks, tilte=album[album_title]), search_by="album_id", query=album[album_id]))
  
  #pagination
  total_pages = int(results.xpath("/data/total_pages//text()"))
  if total_pages > 1:
     current_page = int(results.xpath("/data/page//text()"))
     if current_page < total_pages:
       dir.Append(Function(DirectoryItem(Albums, title="Next Page"), artist_id=artist_id, genre_handle=genre_handle, curator_handle=curator_handle, sort_by=sort_by, sort_dir=sort_dir, page=str(current_page+1)))

  
  
  return dir


