import subprocess
import sys


if sys.platform == "win32":
    import win11toast


# < ----------------------------------------------------------------------- > #


def _notify_linux(message: str, title: str = "") -> None:
    subprocess.run(["notify-send", title, message])


# < ----------------------------------------------------------------------- > #


def _notify_win32(message: str, title: str = "") -> None:
    win11toast.toast(title, message)


# < ----------------------------------------------------------------------- > #


def notify(message: str, title: str = "") -> None:
    match sys.platform:
        case "linux":
            _notify_linux(title, message)

        case "win32":
            _notify_win32(title, message)


# < ----------------------------------------------------------------------- > #
