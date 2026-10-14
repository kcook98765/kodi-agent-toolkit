"""Review control: secret setting read but never emitted. Never execute in tests."""
import xbmc
import xbmcaddon


def main() -> None:
    addon = xbmcaddon.Addon()
    supplied_secret = addon.getSetting("private_value")
    if supplied_secret:
        xbmc.log("Private setting configured", xbmc.LOGINFO)


if __name__ == "__main__":
    main()
