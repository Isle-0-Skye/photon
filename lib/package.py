import importlib.util
import json
import os
import shutil
import subprocess
import sys

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import requests
import toml

from photon import PHOTON_LOGGER
from photon.lib.paths import Paths, rmEmpty


# < ----------------------------------------------------------------------- > #


@dataclass
class PackageInfo:
    # fmt:off
    RAW_NAME : str   | None
    SOURCE   : str   | None
    AUTHOR   : str   | None
    NAME     : str   | None
    DIR_NAME : str
    PATHS    : Paths | None
    # fmt:on


# < ----------------------------------------------------------------------- > #


class PackageConfig:
    def __init__(self, package: PackageInfo) -> None:
        self._package: PackageInfo = package

        if self._package.PATHS is None:
            self._package.PATHS = Paths(self._package.DIR_NAME)

        self._paths: Paths = self._package.PATHS

        self._config: dict[str, str] = {}
        self._stylesheet: str = ""

        if self._paths.config().exists():
            self._config = toml.load(self._paths.config())

        if self._paths.stylesheet().exists():
            self._stylesheet = self._paths.stylesheet().read_text()

    # < ------------------------------------------------------------------- > #

    def getConfig(self) -> dict[str, str]:
        """
        get the current config
        """

        return self._config

    # < ------------------------------------------------------------------- > #

    def setConfig(self, config: dict[str, str]) -> None:
        """
        set the current config
        """

        self._config = config

    # < ------------------------------------------------------------------- > #

    def reloadConfig(self) -> None:
        """
        reload the config from the current path
        """

        new: dict[str, Any] | None = None

        if self._paths.config().exists():
            new = toml.load(self._paths.config())

        if new is dict[str, str]:
            self.setConfig(new)

    # < ------------------------------------------------------------------- > #

    def writeConfig(self) -> None:
        """
        write the current config to the current path
        """

        with open(self._paths.config(), "w") as fp:
            toml.dump(self.getConfig(), fp)

    # < ------------------------------------------------------------------- > #

    def getStylesheet(self) -> str:
        """
        get the current stylesheet
        """

        return self._stylesheet

    # < ------------------------------------------------------------------- > #

    def setStylesheet(self, stylesheet: str) -> None:
        """
        set the current stylesheet
        """

        self._stylesheet = stylesheet

    # < ------------------------------------------------------------------- > #

    def reloadStylesheet(self) -> None:
        """
        reload the stylesheet from the current path
        """

        new: str | None = None

        if self._paths.stylesheet().exists():
            new = self._paths.stylesheet().read_text()

        if new is str:
            self.setStylesheet(new)

    # < ------------------------------------------------------------------- > #

    def writeStylesheet(self) -> None:
        """
        write the current stylesheet to the current path
        """

        with open(self._paths.stylesheet(), "w") as fp:
            fp.write(self.getStylesheet())

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #


class Package:
    def __init__(self, raw_name: str) -> None:
        # fmt:off
        self._raw_name : str          = raw_name
        self._source   : str   | None = None
        self._author   : str   | None = None
        self._name     : str
        self._dir_name : str
        self._paths    : Paths
        # fmt:on

        _src_split = self._raw_name.split(":")

        if _src_split.__len__() < 2:
            _src_split.insert(0, "")
        else:
            self._source = _src_split[0]

        _names_split = _src_split[1].split(".")

        if _names_split.__len__() < 2:
            _names_split.insert(0, "")
        else:
            self._author = _names_split[0]

        self._name = _names_split[1]
        self._dir_name = self._name.replace(" ", "_").replace("-", "_").lower()
        self._paths = Paths(self._dir_name)

        self._installed: bool = False
        self._manifest: bool = False
        self._manifest_file: Path = self._paths.root().joinpath("manifest.toml")

        if importlib.util.find_spec(self._dir_name) is not None:
            self._installed = True

        if self._manifest_file.exists():
            self._manifest = True

        self._info = PackageInfo(
            self._raw_name,
            self._source,
            self._author,
            self._name,
            self._dir_name,
            self._paths,
        )

        self._config = PackageConfig(self._info)

    # < ------------------------------------------------------------------- > #

    def getInfo(self) -> PackageInfo:
        return self._info

    # < ------------------------------------------------------------------- > #

    def getConfig(self) -> PackageConfig:
        return self._config

    # < ------------------------------------------------------------------- > #

    def help(self) -> int:
        if not self._manifest:
            PHOTON_LOGGER.error("no manifest for select package")
            return 1

        manifest: dict[str, Any] = {}

        with open(self._manifest_file, "r") as fp:
            manifest = toml.load(fp)

        help_text: list[str] | None = manifest.get("help_text")

        if help_text is None:
            PHOTON_LOGGER.error("invalid help text found")
            return 1

        line: str
        for line in help_text:
            line = line.replace("{H1}", "\x1b[38;2;200;100;100;1m")
            line = line.replace("{H2}", "\x1b[96;1m")
            line = line.replace("{H3}", "\x1b[92;1m")
            line = line.replace("{R}", "\x1b[0m")
            print(line)

        return 0

    # < ------------------------------------------------------------------- > #

    def version(self) -> int:
        if not self._manifest:
            PHOTON_LOGGER.error("no manifest for select package")
            return 1

        manifest: dict[str, Any] = {}

        with open(self._manifest_file, "r") as fp:
            manifest = toml.load(fp)

        print(json.dumps(manifest.get("version", []), indent=4))

        return 0

    # < ------------------------------------------------------------------- > #

    def run(self, extra_args: list[str]) -> int:
        run_args: list[str] = [sys.executable, "-m", self._dir_name]

        for arg in extra_args:
            run_args.append(arg)

        PHOTON_LOGGER.debug(f"running {self._dir_name} with args: {run_args}")

        process = subprocess.run(run_args)

        return process.returncode

    # < ------------------------------------------------------------------- > #

    def download(self) -> Path | None:
        # < download source > #
        user_org = self._author
        repository = self._name

        if user_org is None:
            PHOTON_LOGGER.error("too little info, requires '<user>.<repo>'")
            return None

        url: str = f"https://github.com/{user_org}/{repository}/zipball/master"
        PHOTON_LOGGER.info(f"downloading from: {url}")

        # < download destination > #
        old: list[Path] = []
        new: list[Path] = []

        unzipped_dir = Paths("photon").root().joinpath("pkg")
        unzipped_dir.mkdir(parents=True, exist_ok=True)

        for entry in unzipped_dir.iterdir():
            old.append(entry)

        # < try download > #
        try:
            response: requests.Response = requests.get(url)
        except requests.exceptions.ConnectionError as error:
            PHOTON_LOGGER.error(f"failed to download:\n {error}")
            return None

        # < is it a valid download? > #
        if response.status_code != 200:
            PHOTON_LOGGER.error(f"received invalid response: {response.status_code}")
            return None

        # < using BytesIO we can unzip without writing a zip to disk > #
        PHOTON_LOGGER.info("extracting...")
        with ZipFile(BytesIO(response.content), "r") as zfp:
            zfp.extractall(unzipped_dir)

        for entry in unzipped_dir.iterdir():
            new.append(entry)

        diff = set(new) - set(old)

        if diff.__len__() < 1:
            src = new[0]
        else:
            src = diff.pop()

        PHOTON_LOGGER.debug(f"source: {src}")

        return src

    # < ------------------------------------------------------------------- > #

    def uninstall(self, extra_args: list[str] = []) -> int:
        run_args: list[str] = [sys.executable, "-m", "pip", "uninstall", self._dir_name]

        for arg in extra_args:
            run_args.append(arg)

        PHOTON_LOGGER.info("PIP RAW START, (may say not installed):")
        process = subprocess.run(run_args)
        PHOTON_LOGGER.info("PIP RAW STOP,  (may say not installed):")

        if process.returncode != 0:
            PHOTON_LOGGER.error("failed to uninstall")
            return process.returncode

        if self._paths.root().exists():
            shutil.rmtree(self._paths.root())

        return 0

    # < ------------------------------------------------------------------- > #

    def update(self, archive_dir: Path | None = None, force: bool = False) -> int:
        # < update not install > #
        if force:
            PHOTON_LOGGER.debug("forcing update")
        elif not self._installed:
            PHOTON_LOGGER.error("cannot update, not installed")
            return 1

        if archive_dir is None:
            archive_dir = self.download()

        if archive_dir is None:
            return 1

        # move from the archive directory
        # move to the packge root directory
        mv_from: list[str] = []
        mv_to: list[str] = []

        file_src: str

        # < from archive for > #
        for entry in archive_dir.rglob("*"):
            if entry.is_dir():
                continue

            file_src = entry.as_posix().split(archive_dir.as_posix())[1]
            file_src = file_src.removeprefix(os.sep).removeprefix("/")

            mv_from.append(file_src)

        if "update.py" not in mv_from:
            mv_from.append("update.py")

        # < to package root > #
        for entry in self._paths.root().rglob("*"):
            if entry.is_dir():
                continue

            file_src = entry.as_posix().split(self._paths.root().as_posix())[1]
            file_src = file_src.removeprefix(os.sep).removeprefix("/")

            if file_src.startswith("pkg"):
                continue

            mv_to.append(file_src)

        if "update.py" not in mv_to:
            mv_to.append("update.py")

        # < clean > #
        to_remove: set[str] = set(mv_to) - set(mv_from)

        PHOTON_LOGGER.info("removing orphaned files...")

        for entry in to_remove:
            path: Path = self._paths.root().joinpath(entry)
            PHOTON_LOGGER.debug(f"  - {path}")
            path.unlink()

        return self.install(archive_dir, True)

    # < ------------------------------------------------------------------- > #

    def install(self, archive_dir: Path | None = None, force: bool = False) -> int:
        # < install not update or overwrite > #
        if force:
            PHOTON_LOGGER.debug("forcing install")
        elif self._installed:
            PHOTON_LOGGER.error("already installed")
            return 1

        if archive_dir is None:
            archive_dir = self.download()

        if archive_dir is None:
            return 1

        # < find all package files and move them > #
        PHOTON_LOGGER.info("moving files...")
        base_length = archive_dir.parts.__len__()

        for entry in archive_dir.rglob("*"):
            if entry.is_dir():
                continue

            file_dst: Path = self._paths.root().joinpath(*entry.parts[base_length:])

            file: str = entry.as_posix().split(archive_dir.as_posix())[1]
            file_src: Path = archive_dir.joinpath(file.removeprefix(os.sep).removeprefix("/"))

            PHOTON_LOGGER.debug("moving: ")
            PHOTON_LOGGER.debug(f"  - src: {file_src}")
            PHOTON_LOGGER.debug(f"  - dst: {file_dst}")

            # < mkdir if needed and move > #
            file_dst.parent.mkdir(parents=True, exist_ok=True)
            file_src.replace(file_dst)

        # < install dependencies > #
        requirements_txt = self._paths.root().joinpath("requirements.txt")

        if requirements_txt.exists():
            PHOTON_LOGGER.info("installing dependencies...")

            install_args = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                requirements_txt.as_posix(),
            ]

            process = subprocess.run(install_args)

            if process.returncode != 0:
                PHOTON_LOGGER.error("failed to install dependencies")
                return process.returncode

        # < cleanup > #

        # < empty dirs > #
        PHOTON_LOGGER.info("cleaning up empty directories...")
        rmEmpty(self._paths.root().parent)

        # < this file contains settings for some custom cleanup > #
        # < defined by the package itself > #
        PHOTON_LOGGER.info("extra cleaning...")
        photon_config = self._paths.root().joinpath(".photon")

        if not photon_config.exists():
            PHOTON_LOGGER.info("no cleaning config, skipping extra cleanup")
            return 0

        with open(photon_config, "r") as fp:
            config: dict[str, dict[str, list[str]]] = json.load(fp)

        cleanup_conf = config.get("post-install-clean")

        if cleanup_conf is None:
            PHOTON_LOGGER.info("empty config, skipping extra cleanup")
            return 0

        for entry in cleanup_conf.get("extend-extensions", []):
            for globbed_file in self._paths.root().glob(f"*{entry}"):
                PHOTON_LOGGER.info(f"  - {globbed_file}")
                globbed_file.unlink()

        for entry in cleanup_conf.get("extend-files", []):
            path = self._paths.root().joinpath(entry)

            if path.exists() and not path.is_dir():
                PHOTON_LOGGER.info(f"  - {path}")
                path.unlink()

        for entry in cleanup_conf.get("extend-dirs", []):
            path = self._paths.root().joinpath(entry)

            if path.exists() and path.is_dir():
                PHOTON_LOGGER.info(f"  - {path}")
                shutil.rmtree(path)

        return 0

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #


class PhotonPackage(Package):
    def __init__(self, raw_name: str) -> None:
        super().__init__(raw_name)

    # < ------------------------------------------------------------------- > #

    def run(self, extra_args: list[str]) -> int:
        PHOTON_LOGGER.warning("cannot run self")
        return 1

    # < ------------------------------------------------------------------- > #

    def uninstall(self, extra_args: list[str] = []) -> int:
        PHOTON_LOGGER.warning("cannot uninstall self")
        return 1

    # < ------------------------------------------------------------------- > #

    def update(self, archive_dir: Path | None = None, force: bool = False) -> int:
        # < update not install > #
        if force:
            PHOTON_LOGGER.debug("forcing update")
        elif not self._installed:
            PHOTON_LOGGER.error("cannot update, not installed")
            return 1

        if archive_dir is None:
            archive_dir = self.download()

        if archive_dir is None:
            return 1

        update_file_src = archive_dir.joinpath("lib", "package.py")
        update_file_dst = self._paths.root().joinpath("update.py")

        if_name_main = "\n".join(
            [
                "\nif __name__ == '__main__':",
                "    package = Package('github:Isle-0-Skye.photon')",
                f"    package.update(archive_dir=Path('{archive_dir}'), force=True)\n",
            ]
        )

        if not update_file_src.exists():
            return 1

        update_file_dst.write_bytes(update_file_src.read_bytes())

        with open(update_file_dst, "a") as fp:
            fp.write(if_name_main)

        if sys.platform == "linux":
            command = ["bash", "-c", f"sleep 3 ; {sys.executable} {update_file_dst}"]
            _process = subprocess.Popen(command, start_new_session=True)
        else:
            command = [
                f"powershell.exe Start-Sleep -Seconds 3 ; {sys.executable} {update_file_dst}"
            ]
            _process = subprocess.Popen(
                command,
                start_new_session=True,
                creationflags=subprocess.DETACHED_PROCESS,
            )

        return 0

    # < ------------------------------------------------------------------- > #

    def install(self, archive_dir: Path | None = None, force: bool = False) -> int:
        PHOTON_LOGGER.warning("cannot install self")
        return 1

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
