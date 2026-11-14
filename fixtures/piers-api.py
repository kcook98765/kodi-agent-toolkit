"""Static-only APIs compared to pinned Kodi Piers RC2 source; never execute."""
import xbmc
import xbmcgui

item = xbmcgui.ListItem(label="Piers", offscreen=True)
item.setFileTitle("Piers RC2")
item.setCount(2)
item.setSize(4096)
item.setOverlay(xbmcgui.ICON_OVERLAY_WATCHED)
video = item.getVideoInfoTag()
video.setTitle("Piers")
video.setAvailableFanart([{"image": "https://example.org/fanart.jpg"}])
video.addSeason(1, "Season One", plot="RC2 season plot")
video.addSeasons([(2, "Season Two", "Another plot")])
accepted: bool = video.setOriginalLanguage("eng")
language: str = video.getOriginalLanguage()
stream = xbmc.VideoStreamDetail(width=1920, height=1080, hdrtype="dolbyvision", hdrdetail="8.4")
stream.setHDRDetail("7FEL")
hdr: str = stream.getHDRDetail()
video.addVideoStream(stream)

# These twelve methods were added after the official RC1 tag. The published
# prerelease stubs already contain them; compare their signatures to exact RC2.
game = item.getGameInfoTag()
game.setOriginalTitle("Original")
game.setRating(8.5)
game.setPlayers(2)
game.setAgeRating("PEGI 12")
game.setTrailer("https://example.org/trailer")
game.setTags(["Adventure"])
original: str = game.getOriginalTitle()
rating: float = game.getRating()
players: int = game.getPlayers()
age: str = game.getAgeRating()
trailer: str = game.getTrailer()
tags: list[str] = game.getTags()
xbmc.log("Static fixture", xbmc.LOGINFO)
