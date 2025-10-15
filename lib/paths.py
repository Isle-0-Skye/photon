import importlib.util

from importlib.machinery import ModuleSpec
from pathlib import Path

from photon import PHOTON_LOGGER


# < ----------------------------------------------------------------------- > #


def pathToParents(path: Path, parents: int = 1) -> Path:
    """
    add parents to a path
    """

    len: int = path.parts.__len__()

    if len > 2:
        len = len - 1 - parents

    return Path(*path.parts[len:])


# < ----------------------------------------------------------------------- > #


def rmEmpty(path: Path) -> None:
    """
    recursively delete empty directories
    """

    for entry in path.iterdir():
        if entry.is_dir():
            rmEmpty(entry)
        else:
            continue

        try:
            entry.rmdir()
        except OSError:
            continue


# < ----------------------------------------------------------------------- > #


def find_module_root(pkg: str) -> Path | None:
    """
    find the root or origin of a module
    """

    spec: ModuleSpec | None = importlib.util.find_spec(pkg)

    if spec is None:
        return None

    if spec.origin is None:
        return None

    return Path(spec.origin).parent


# < ----------------------------------------------------------------------- > #


class Paths:
    def __init__(self, pkg: str) -> None:
        self.pkg: str = pkg
        self.pkg_root: Path = self.root()

    # < ------------------------------------------------------------------- > #

    def setRoot(self, path: Path) -> None:
        self.pkg_root = path

    # < ------------------------------------------------------------------- > #

    def root(self) -> Path:
        if hasattr(self, "pkg_root"):
            return self.pkg_root

        root: None | Path = find_module_root(self.pkg)

        if root is None:
            PHOTON_LOGGER.warning("could not find root, using alternate method")
            new_root = Path(__file__).parent.parent.parent.joinpath(self.pkg)
            PHOTON_LOGGER.debug(new_root)
            return new_root

        self.pkg_root = root
        return root

    # < ------------------------------------------------------------------- > #

    def resources(self) -> Path:
        return self.root().joinpath("resources")

    # < ------------------------------------------------------------------- > #

    def fonts(self) -> Path:
        return self.resources().joinpath("fonts")

    # < ------------------------------------------------------------------- > #

    def images(self) -> Path:
        return self.resources().joinpath("images")

    # < ------------------------------------------------------------------- > #

    def sounds(self) -> Path:
        return self.resources().joinpath("sounds")

    # < ------------------------------------------------------------------- > #

    def videos(self) -> Path:
        return self.resources().joinpath("videos")

    # < ------------------------------------------------------------------- > #

    def settings(self) -> Path:
        return self.root().joinpath("settings")

    # < ------------------------------------------------------------------- > #

    def config(self) -> Path:
        return self.settings().joinpath("settings.toml")

    # < ------------------------------------------------------------------- > #

    def manifest(self) -> Path:
        return self.settings().joinpath("manifest.toml")

    # < ------------------------------------------------------------------- > #

    def stylesheet(self) -> Path:
        return self.settings().joinpath("stylesheet.css")

    # < ------------------------------------------------------------------- > #

    def all(self) -> dict[str, str]:
        # fmt: off
        return {
            "root"       : self.root()       .as_uri(),
            "resources"  : self.resources()  .as_uri(),
            "fonts"      : self.fonts()      .as_uri(),
            "images"     : self.images()     .as_uri(),
            "sounds"     : self.sounds()     .as_uri(),
            "videos"     : self.videos()     .as_uri(),
            "settings"   : self.settings()   .as_uri(),
            "config"     : self.config()     .as_uri(),
            "manifest"   : self.manifest()   .as_uri(),
            "stylesheet" : self.stylesheet() .as_uri(),
        }
        # fmt: on

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
