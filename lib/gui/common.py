from pathlib import Path

from photon import PHOTON_LOGGER


# < ----------------------------------------------------------------------- > #


class FontVault:
    def __init__(self, path: Path) -> None:
        self.supported_formats: list[str] = ["otf", "ttf", "woff", "woff2"]
        self.fonts: dict[str, Path] = {}

        if path.exists():
            self.loadFromPath(path)

    # < ------------------------------------------------------------------- > #

    def getFontDict(self) -> dict[str, Path]:
        """
        get the current dict of fonts \n
        none are guarenteed to be loaded or valid beyond the file extension
        """

        return self.fonts

    # < ------------------------------------------------------------------- > #

    def loadFromPath(self, path: Path) -> None:
        """
        recursively search for fonts in the given path
        """

        if not path.exists():
            return None

        for entry in path.iterdir():
            if entry.is_dir():
                self.loadFromPath(entry)
            elif entry.is_file():
                self.filterFile(entry)

    # < ------------------------------------------------------------------- > #

    def filterFile(self, file: Path) -> None:
        """
        add a file to the internal dict only if it is a supported format
        """

        try:
            file_extension: str = file.name.rsplit(".", 1)[1]
        except IndexError:
            PHOTON_LOGGER.debug(f"invalid file given, failed to split {file.name} for extension")
            return None

        if file_extension in self.supported_formats:
            PHOTON_LOGGER.debug(f"adding new font: {file.stem} from {file}")
            self.fonts[file.stem] = file

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
