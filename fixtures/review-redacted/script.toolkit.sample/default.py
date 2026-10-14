"""Holdout: transformed setting is never emitted. Never execute in tests."""
import xbmc
import xbmcaddon


def main() -> None:
    config = xbmcaddon.Addon()
    token = config.getSetting("private_value")
    token = "[redacted]" if token else "[not configured]"
    xbmc.log(token, xbmc.LOGINFO)


if __name__ == "__main__":
    main()
