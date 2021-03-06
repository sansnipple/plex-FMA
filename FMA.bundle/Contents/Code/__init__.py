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
  Plugin.AddPrefixHandler(FMA_PREFIX, MainMenu, 'The Free Music Archive', 'icon-default.png', 'art-default.png')
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.title1 = 'Free Music Archive'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.png')
  DirectoryItem.thumb=R('icon-default.png')
  InputDirectoryItem.thumb=R('icon-default.png')
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################

def CreateDict():
  Dict.Set("artists", [])


def UpdateCache():
  
  # use this to grab the all artists list and save to the plugin Dict
  # lets hope i designed this looping right, it'll be a pain to change later
  
  artists = []
  page = 1
  total_pages = 1
  while page <= total_pages:
    url = API_ROOT + "artists.xml?limit=50&sort_by=artist_handle&sort_dir=asc&page=" + str(page)
    results = XML.ElementFromURL(url , errors="ignore", cacheTime=CACHE_1DAY)
    for i in range(len(results.xpath("//dataset/value"))):
      artist                  = {}
      artist["artist_id"]     = results.xpath("//dataset/value[%i]/artist_id//text()" % (i+1))[0]
      artist["artist_handle"] = results.xpath("//dataset/value[%i]/artist_handle//text()" % (i+1))[0]
      artist["artist_name"]   = results.xpath("//dataset/value[%i]/artist_name//text()" % (i+1))[0]
      try:
        artist["artist_bio"]    = results.xpath("//dataset/value[%i]/artist_bio//text()" % (i+1))[0]
      except: artist["artist_bio"] = "No Information Availible"
      # images here later hopefully
      artists.append(artist)
      
    total_pages = int(results.xpath("/data/total_pages//text()")[0])
    current_page = int(results.xpath("/data/page//text()")[0])
    page = current_page + 1
    if current_page < total_pages:
      continue
    else:
      break

  Dict.Set("artists", artists)

#####################

def MainMenu():
  dir = MediaContainer(viewGroup='List')
  dir.Append(Function(DirectoryItem(Artists, title="All Artists...")))
  dir.Append(Function(DirectoryItem(RSS, title="Most Interesting Highlights"), url = "http://freemusicarchive.org/interesting.atom"))
  dir.Append(Function(DirectoryItem(RSS, title="Recently Added Hightlights"), url = "http://freemusicarchive.org/recent.atom"))
  dir.Append(Function(DirectoryItem(ResetDict, title="do not pass go"))) # for debugging so dont have to manually nuke the dict every time
  return dir

##################################################################################################

# for debugging only 
def ResetDict(sender):
  dir = MediaContainer(viewGroup='List')
  Dict.Reset()
  UpdateCache()
  return MessageContainer("blammo", "Dict Reset")



def Tracks(sender, search_by="", query="", sort_by="", sort_dir="", page="1"):
  dir = MediaContainer(viewGroup='List')
  url = API_ROOT + "tracks.xml?" + search_by + "=" + query + "&limit=50" + "&page=" + page + "&sort_by=" + sort_by + "&sort_dir=" + sort_dir
  
  # lxml objectify is fucking awesome!
  
  data = XML.ObjectFromURL(url)
  try:
    for track in data.dataset.value:
      dir.Append(Function(TrackItem(getTrack, title=track.track_title, artist=track.artist_name, album=track.album_title), ext="mp3", url=track.track_url.pyval))
  except:
    return MessageContainer("Empty", "No Tracks were found for the requested parameters")  
  # pagination
  if data.total_pages > 1:
    if data.page < data.total_pages:
      dir.Append(Function(DirectoryItem(Tracks, title="Next Page"), search_by=search_by, query=query, sort_by=sort_by, sort_dir=sort_dir, page=str(data.page.pyval + 1)))

  return dir

def getTrack(sender, url=''):
  """Get the actual mp3 url by scraping the track's html page"""
  page  = XML.ElementFromURL(url, isHTML=True)
  finalURL = page.xpath("//a[@title='Download']/@href")[0]
  
  return Redirect(finalURL)

def Albums(sender, artist_id="", genre_handle="", curator_handle="", page = "1",  sort_by="", sort_dir=""):
  dir = MediaContainer(viewGroup='List')
  url = API_ROOT + "albums.xml?artist_id=" + artist_id + "&genre_handle=" + genre_handle + "&curator_handle=" + curator_handle + "&limit=50" + "&page=" + page + "&sort_by=" + sort_by + "&sort_dir=" + sort_dir
  data = XML.ObjectFromURL(url)
  try:
    for album in data.dataset.value:
      dir.Append(Function(DirectoryItem(Tracks, title=album.album_title), search_by="album_id", query=album.album_id.text, sort_by="track_number"))
  except:
    if artist_id:
      return Tracks(sender, search_by='artist_id', query=artist_id)   # stopgap catch for artists with no albums, need to make it more robust later
  
  #pagination
  if data.total_pages > 1:
    if data.page < data.total_pages:
      dir.Append(Function(DirectoryItem(Albums, title="Next Page"), artist_id=artist_id, genre_handle=genre_handle, curator_handle=curator_handle, sort_by=sort_by, sort_dir=sort_dir, page=str(data.page.pyval + 1)))
      
  return dir


def Artists(sender, sort_by="artist_handle", sort_dir=""):
  dir = MediaContainer(viewGroup='List')
  

  # i should also split by letter like i did with LMA
  artists = Dict.Get("artists")
  if artists == []:
    return MessageContainer("oh god the blood!", "sorry an error has occured \nlikely the artists list just isnt populated yet \nwait a bit and try again")
  for artist in artists:
    dir.Append(Function(DirectoryItem(Albums, title=artist["artist_name"]), artist_id=artist["artist_id"]))
  
  return dir

def RSS(sender, url=''):
  dir = MediaContainer(viewGroup='List', title2=sender.itemTitle)
  # wish these feeds contained id numbers i could link them with the api for fuller metadata, but i can work with what i've got
  feed = XML.ElementFromURL(url, isHTML=True, errors='ignore')
  for i in range(len(feed.xpath("//entry"))):
    title = feed.xpath("//entry[%i]/title//text()" % (i+1))[0]
    title = title.split(" : ", )
    artist_name = title[0]
    album_title = title[1]
    track_title = title[2]
    track_url = feed.xpath("//entry[%i]/link[@rel='alternate']/@href" % (i+1))[0]
    # maybe later try to parse a artist handle out of this somewhere to get a usable context key
    dir.Append(Function(TrackItem(getTrack, title=track_title, artist=artist_name, album=album_title), ext="mp3", url=track_url))
  return dir


