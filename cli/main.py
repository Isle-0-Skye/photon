import sys

from dataclasses import dataclass
from enum import Enum

from photon import PHOTON_LOGGER
from photon.lib.notify import notify
from photon.lib.package import Package, PhotonPackage


# < ----------------------------------------------------------------------- > #


class Mode(Enum):
    # fmt:off
    HELP      = 0
    VERSION   = 1
    RUN       = 2
    UPDATE    = 3
    INSTALL   = 4
    UNINSTALL = 5
    # fmt:on


# < ----------------------------------------------------------------------- > #


@dataclass
class Settings:
    MODE: Mode
    PACKAGE: Package
    LOG_LEVEL: int = 20


# < ----------------------------------------------------------------------- > #


def strToLogInt(level: str) -> int:
    match level.upper():
        case "DEBUG":
            return 10

        case "INFO":
            return 20

        case "WARNING":
            return 30

        case "ERROR":
            return 40

        case "CRITICAL":
            return 50

        case _:
            PHOTON_LOGGER.debug("unknown log level, fallback to 0")
            return 0


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
        "--log-level",
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
    package: Package | PhotonPackage
    if sys.argv[2].endswith(".photon"):
        PHOTON_LOGGER.info("using alternative package class")
        package = PhotonPackage(sys.argv[2])
    else:
        package = Package(sys.argv[2])

    # < settings for photon > #
    settings = Settings(mode, package)

    # < split args between photon and the package > #
    # < -- is used to split > #
    photon_args: dict[str, str] = {}
    package_args: list[str] = []

    index = 2
    skip_next = False
    stop = False
    for_photon = True

    for arg in sys.argv[3:]:
        index = index + 1

        if skip_next:
            skip_next = False
            continue

        if arg == "--":
            for_photon = False
            continue

        if for_photon and arg in supported_options:
            photon_args[arg] = sys.argv[index + 1]
            skip_next = True
        elif for_photon:
            PHOTON_LOGGER.warning(f"unsupported option: {arg}")
            stop = True
        else:
            package_args.append(arg)

    if stop:
        return 1

    # < set photons log level > #
    if "--log-level" in photon_args:
        log_level = photon_args["--log-level"]
        log_int = strToLogInt(log_level)

        settings.LOG_LEVEL = log_int

    PHOTON_LOGGER.setLevel(settings.LOG_LEVEL)

    # < useful info for debugging > #
    PHOTON_LOGGER.debug(f"running photon with args: {photon_args}")
    PHOTON_LOGGER.debug(settings)
    PHOTON_LOGGER.debug(f"running package with args: {package_args}")

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
