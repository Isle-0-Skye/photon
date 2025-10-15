import sys

from dataclasses import dataclass
from enum import Enum

from photon import PHOTON_LOGGER
from photon.lib.notify import notify
from photon.lib.package import Package


# < ----------------------------------------------------------------------- > #


class Mode(Enum):
    HELP = 0
    VERSION = 1
    RUN = 2
    UPDATE = 3
    INSTALL = 4
    UNINSTALL = 5


# < ----------------------------------------------------------------------- > #


@dataclass
class Settings:
    MODE: Mode
    PACKAGE: Package


# < ----------------------------------------------------------------------- > #


def strToMode(mode: str) -> Mode:
    match mode:
        case "run":
            return Mode.RUN

        case "version":
            return Mode.VERSION

        case "help":
            return Mode.HELP

        case "update":
            return Mode.UPDATE

        case "install":
            return Mode.INSTALL

        case "uninstall":
            return Mode.UNINSTALL

        case _:
            PHOTON_LOGGER.debug("unknown run mode, fallback to help")
            return Mode.HELP


# < ----------------------------------------------------------------------- > #


def main() -> int:
    supported_modes: list[str] = [
        "run",
        "version",
        "help",
        "update",
        "install",
        "uninstall",
    ]

    supported_options: list[str] = [
        "--package",
    ]

    # < [0] / 1: path to __main__.py file > #
    # < [1] / 2: mode > #
    # < [2] / 3: package > #
    # < less than three means mode or package are missing > #
    if sys.argv.__len__() < 3:
        PHOTON_LOGGER.warning("too few arguments")
        return 1

    # < filter out invalid modes > #
    if sys.argv[1] not in supported_modes:
        PHOTON_LOGGER.warning("unsupported mode")
        return 1
    else:
        mode: Mode = strToMode(sys.argv[1])

    # < package to run > #
    package = Package(sys.argv[2])
    settings = Settings(mode, package)

    # < split args between photon and the package > #
    # < -- is used to split > #
    photon_args: list[str] = []
    package_args: list[str] = []

    for_photon = True

    for arg in sys.argv[3:]:
        if arg == "--":
            for_photon = False
            continue

        if for_photon and arg in supported_options:
            photon_args.append(arg)
        elif for_photon:
            PHOTON_LOGGER.warning(f"unsupported option: {arg}")
            return 1
        else:
            package_args.append(arg)

    # < run program in desired mode > #
    match settings.MODE:
        case Mode.RUN:
            return package.run(package_args)

        case Mode.VERSION:
            return package.version()

        case Mode.HELP:
            return package.help()

        case Mode.UPDATE:
            if package.update():
                return 1
            else:
                notify(f"{package.getInfo().NAME} has been updated")
                return 0

        case Mode.INSTALL:
            if package.install():
                return 1
            else:
                notify(f"{package.getInfo().NAME} has been installed")
                return 0

        case Mode.UNINSTALL:
            if package.uninstall():
                return 1
            else:
                notify(f"{package.getInfo().NAME} has been uninstalled")
                return 0


# < ----------------------------------------------------------------------- > #
