"""Deliberately unsafe review fixture; never execute in Kodi."""
import xbmc
import xbmcaddon


def main() -> None:
    addon = xbmcaddon.Addon()
    supplied_secret = addon.getSetting("private_value")
    xbmc.log(supplied_secret, xbmc.LOGINFO)


if __name__ == "__main__":
    main()
