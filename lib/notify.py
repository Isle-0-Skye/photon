import subprocess
import sys
import time

from photon import PHOTON_LOGGER


if sys.platform == "win32":
    import win11toast


# < ----------------------------------------------------------------------- > #


def _notify_linux(message: str, title: str = "") -> None:
    subprocess.run(["notify-send", title, message])


# < ----------------------------------------------------------------------- > #


def _notify_win32(message: str, title: str = "") -> None:
    win11toast.toast(title, message)


# < ----------------------------------------------------------------------- > #


def notify(message: str, title: str = "", sleep: int = 3) -> None:
    time.sleep(sleep)
    match sys.platform:
        case "linux":
            _notify_linux(title, message)

        case "win32":
            _notify_win32(title, message)

        case _:
            PHOTON_LOGGER.warning("unsupported notify platform")


# < ----------------------------------------------------------------------- > #
