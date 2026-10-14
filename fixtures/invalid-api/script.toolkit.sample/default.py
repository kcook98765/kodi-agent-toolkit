"""Disposable sample: Kodi provides these runtime modules."""
import xbmc


def main() -> None:
    """Log a fixed nonprivate diagnostic when Kodi runs this script."""
    xbmc.log("Toolkit sample ready", "info")


if __name__ == "__main__":
    main()
