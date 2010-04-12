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


LMA_PREFIX   = "/music/FMA"

CACHE_INTERVAL = 3600


###################################################################################################
def Start():
  Plugin.AddPrefixHandler(LMA_PREFIX, MainMenu, 'Free Music Archive', 'icon-default.png', 'art-default.png')
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


