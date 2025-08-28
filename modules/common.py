def print_import_error(
    import_tree: str,
    error: ImportError,
    hypertext: bool = True,
    import_type: str = "installed",
    link: str | None = None,
    text: str | None = None,
):
    print(
        f"{import_type} import error: {import_tree}",
        f"  {error.args[0].split('(')[0]}",
        sep=os.linesep,
    )
    if hypertext:
        hyperlink = f"\x1b]8;{''};{link}\x1b\\{text}\x1b]8;;\x1b\\"
        print(f"  is {hyperlink} installed?")
    sys.exit(1)


# < pre installed imports --------------------------------------------------------------------- > #
import logging
import os
import sys

from pathlib import Path


# < not pre installed imports ----------------------------------------------------------------- > #
try:
    import yaml
except ImportError as error:
    print_import_error(
        import_tree="[common]<-[yaml]",
        error=error,
        link="https://pypi.org/project/PyYAML",
        text="PyYAML",
    )


# < shared between photon, modules and packages ----------------------------------------------- > #
class universals:
    """
    used to share basic data between photon, modules and packages\n
    this contains commonly used information such as project roots
    """

    def __init__(self) -> None:
        super().__init__()

        # < path of this files parent directory > #
        # self.PHOTON_ROOT = os.path.realpath(__file__).rsplit(os.sep, 2)[0]
        self.PHOTON_ROOT = Path(__file__).resolve().parent.parent

        # < load style file > #
        photon_style_file = Path(self.PHOTON_ROOT, "style.yaml")
        if not photon_style_file.exists():
            print("Error: Failed to read style file, does style.yaml exist?")
            sys.exit(1)

        with open(photon_style_file, "r") as style_file:
            self.STYLES: dict = yaml.safe_load(style_file)

        # < default log level > #
        self.LOG_LEVEL = 20

    def root(self) -> Path:
        """
        returns the directory that contains photons main.py
        """

        return self.PHOTON_ROOT

    def package_root(self, package) -> Path:
        """
        returns a packages root within photons package directory
        """

        return Path(self.PHOTON_ROOT, "packages", package)

    def set_log_level(self, level: int) -> None:
        """
        sets the log_level variable \n
        it is up to the project to re-read the value
        """

        self.LOG_LEVEL = level

    def log_level(self) -> int:
        """
        returns the value of the current log_level
        """

        return self.LOG_LEVEL

    def styles(self, key) -> str:
        return self.STYLES.get(key, "")


UNIVERSALS = universals()


# < formats any logged message for the photon logger ------------------------------------------ > #
class customFormatter(logging.Formatter):
    """
    formats any logged message for the photon logger
    """

    _ld = UNIVERSALS.styles("log_debug")
    _li = UNIVERSALS.styles("log_info")
    _lw = UNIVERSALS.styles("log_warning")
    _le = UNIVERSALS.styles("log_error")
    _lc = UNIVERSALS.styles("log_critical")
    _lr = UNIVERSALS.styles("reset")

    asctime = "%(asctime)s"
    filename_lineno = "%(filename)s:%(lineno)s"

    time = f"{_ld}[{asctime}]{_lr}"
    level = "%(levelname)s"
    file_and_line = f"{_ld}[{filename_lineno}]{_lr}"
    text = "%(message)s"

    FORMATS = {
        logging.DEBUG: f"{time} {_ld}[{level}---]{_lr} {file_and_line} {_ld}{text}{_lr}",
        logging.INFO: f"{time} {_li}[{level}----]{_lr} {file_and_line} {_li}{text}{_lr}",
        logging.WARNING: f"{time} {_lw}[{level}-]{_lr} {file_and_line} {_lw}{text}{_lr}",
        logging.ERROR: f"{time} {_le}[{level}---]{_lr} {file_and_line} {_le}{text}{_lr}",
        logging.CRITICAL: f"{time} {_lc}[{level}]{_lr} {file_and_line} {_lc}{text}{_lr}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)


# < photons logger ---------------------------------------------------------------------------- > #
def logger(log_level: str | int = logging.DEBUG) -> logging.Logger:
    """
    photons logger
    """

    logger = logging.getLogger("photon_logger")
    logger.setLevel(logging.DEBUG)

    custom_handler = logging.StreamHandler(sys.stdout)
    custom_handler.setLevel(log_level)

    custom_formatter = customFormatter()
    custom_handler.setFormatter(custom_formatter)

    if not logger.handlers:
        logger.addHandler(custom_handler)

    return logger


pLOG = logger(UNIVERSALS.log_level())
# < ------------------------------------------------------------------------------------------- > #


# < formats text into hyperlink text ---------------------------------------------------------- > #
def text_to_hypertext(link: str, text: str) -> str:
    """
    formats text into hyperlink text
    """

    return f"\x1b]8;{''};{link}\x1b\\{text}\x1b]8;;\x1b\\"
