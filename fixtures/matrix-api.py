"""Static-only Kodi 19.5 API fixture. Never execute outside Kodi."""
import xbmc
import xbmcgui
import xbmcvfs

item = xbmcgui.ListItem(label="Matrix")
item.setInfo("video", {"title": "Matrix", "year": 2024, "rating": 8.5,
                       "genre": ["Comedy"], "castandrole": [("Actor", "Role")]})
item.setCast([{"name": "Actor", "role": "Role", "order": 1}])
item.setUniqueIDs({"imdb": "tt0000001"}, "imdb")
path: str = xbmcvfs.translatePath("special://profile/")
xbmc.log(path, xbmc.LOGINFO)
