from dataclasses import dataclass
from pathlib import Path

from photon import PHOTON_LOGGER
from photon.lib.gui.common import FontVault
from photon.lib.paths import Paths
from PySide6.QtGui import QFontDatabase, QIcon, QPixmap


# < ----------------------------------------------------------------------- > #


class QFontVault(FontVault):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

        if path.exists():
            self.loadFromPath(path)

        self.reloadFontDatabase()

    # < ------------------------------------------------------------------- > #

    def reloadFontDatabase(self) -> None:
        for font in self.fonts.values():
            PHOTON_LOGGER.debug(f"adding application font: {font.name}")
            QFontDatabase.addApplicationFont(font.as_posix())

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #


@dataclass
class ImageData:
    path: Path
    name: str
    qpixmap: QPixmap | None
    qicon: QIcon | None


# < ----------------------------------------------------------------------- > #


class QImageVault:
    def __init__(self) -> None:
        self.images: dict[str, ImageData] = {}

        for image in Paths("photon").images().iterdir():
            PHOTON_LOGGER.debug(f"adding new image {image.stem}")
            self.images[image.stem] = ImageData(image, image.stem, None, None)

        self.default_image: ImageData = self.images["default"]
        PHOTON_LOGGER.debug(f"default image set to {self.default_image}")

    # < ------------------------------------------------------------------- > #

    def loadFromPath(self, path: Path) -> None:
        for image in path.iterdir():
            PHOTON_LOGGER.debug(f"adding new image {image.stem}")
            self.images[image.stem] = ImageData(image, image.stem, None, None)

    # < ------------------------------------------------------------------- > #

    def getDefaultImagePath(self) -> Path:
        return self.default_image.path

    # < ------------------------------------------------------------------- > #

    def getDefaultImageIcon(self) -> QIcon:
        img: ImageData = self.default_image

        if img.qicon is None:
            PHOTON_LOGGER.debug("generating new QIcon")
            img.qicon = QIcon()
            img.qicon.addFile(self.getDefaultImagePath().as_posix())

        return img.qicon

    # < ------------------------------------------------------------------- > #

    def getDefaultImagePixmap(self) -> QPixmap:
        img: ImageData = self.default_image

        if img.qpixmap is None:
            PHOTON_LOGGER.debug("generating new QPixmap")
            img.qpixmap = QPixmap()
            img.qpixmap.load(self.getDefaultImagePath().as_posix())

        return img.qpixmap

    # < ------------------------------------------------------------------- > #

    def getImagePath(self, image: str) -> Path:
        img: ImageData | None = self.images.get(image)

        if img is None:
            PHOTON_LOGGER.warning(f"failed to find image {image}, using default")
            return self.getDefaultImagePath()

        return img.path

    # < ------------------------------------------------------------------- > #

    def getImageIcon(self, image: str) -> QIcon:
        img: ImageData | None = self.images.get(image)

        if img is None:
            PHOTON_LOGGER.warning(f"failed to find image {image}, using default")
            return self.getDefaultImageIcon()

        if img.qicon is None:
            PHOTON_LOGGER.debug("generating new QIcon")
            img.qicon = QIcon()
            img.qicon.addFile(img.path.as_posix())

        return img.qicon

    # < ------------------------------------------------------------------- > #

    def getImagePixmap(self, image: str) -> QPixmap:
        img: ImageData | None = self.images.get(image)

        if img is None:
            PHOTON_LOGGER.warning(f"failed to find image {image}, using default")
            return self.getDefaultImagePixmap()

        if img.qpixmap is None:
            PHOTON_LOGGER.debug("generating new QPixmap")
            img.qpixmap = QPixmap()
            img.qpixmap.load(img.path.as_posix())

        return img.qpixmap

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
