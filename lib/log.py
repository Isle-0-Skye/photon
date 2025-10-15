import inspect
import logging

from pathlib import Path


# < ----------------------------------------------------------------------- > #


def pathToParents(path: Path, parents: int = 1) -> Path:
    """
    add parents to a path \n
    this is a copy of photon.lib.paths.pathToParents \n
    it stops a circular import and keeps existing imports to the stdlib
    """

    len: int = path.parts.__len__()

    if len > 2:
        len = len - 1 - parents

    return Path(*path.parts[len:])


# < ----------------------------------------------------------------------- > #


class ColourFormatter(logging.Formatter):
    # fmt: off
    GREY    : str = "\x1b[90;1m"
    RED     : str = "\x1b[91;1m"
    GREEN   : str = "\x1b[92;1m"
    YELLOW  : str = "\x1b[93;1m"
    BLUE    : str = "\x1b[94;1m"
    MAGENTA : str = "\x1b[95;1m"
    CYAN    : str = "\x1b[96;1m"

    RESET   : str = "\x1b[0m"
    # fmt: on

    message_format: str = (
        "[%(asctime)s] [%(levelname)8s] [%(file)s:%(line)s] [%(func)s()] - %(message)s"
    )

    date_format: str = "%H:%M:%S"

    # fmt: off
    FORMATS: dict[int, str] = {
        logging.DEBUG    : CYAN   + message_format + RESET,
        logging.INFO     : GREEN  + message_format + RESET,
        logging.WARNING  : YELLOW + message_format + RESET,
        logging.ERROR    : RED    + message_format + RESET,
        logging.CRITICAL : RED    + message_format + RESET,
    }
    # fmt: on

    # < ------------------------------------------------------------------- > #

    def format(self, record: logging.LogRecord) -> str:
        defaults: dict[str, str] = {"file": "file", "line": "line", "func": "func"}
        fmt: str = self.FORMATS.get(record.levelno, self.message_format)
        return logging.Formatter(fmt, self.date_format, defaults=defaults).format(record)

    # < ------------------------------------------------------------------- > #

    def setMessageFormat(self, message_format: str) -> None:
        self.message_format = message_format

    # < ------------------------------------------------------------------- > #

    def setDateFormat(self, date_format: str) -> None:
        self.date_format = date_format

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #


class Logger:
    def __init__(self, level: int = 0, name: str | None = None) -> None:
        self.root: logging.Logger
        if name is None:
            self.root = logging.getLogger()
        else:
            self.root = logging.getLogger(name)

        self.root.setLevel(level)

        self.stream_handler: logging.StreamHandler[logging.TextIO] = logging.StreamHandler()

        self.stream_handler.setFormatter(ColourFormatter())

        if not self.root.hasHandlers():
            self.root.addHandler(self.stream_handler)

    # < ------------------------------------------------------------------- > #

    def setLevel(self, level: int) -> None:
        self.root.setLevel(level)

    # < ------------------------------------------------------------------- > #

    def debug(self, msg: object) -> None:
        stack: inspect.FrameInfo = inspect.stack()[1]

        func: str = stack.function
        file: Path = pathToParents(Path(stack.filename))
        line: int = stack.lineno

        self.root.debug(msg, extra={"func": func, "file": file, "line": line})

    # < ------------------------------------------------------------------- > #

    def info(self, msg: object) -> None:
        stack: inspect.FrameInfo = inspect.stack()[1]

        func: str = stack.function
        file: Path = pathToParents(Path(stack.filename))
        line: int = stack.lineno

        self.root.info(msg, extra={"func": func, "file": file, "line": line})

    # < ------------------------------------------------------------------- > #

    def warning(self, msg: object) -> None:
        stack: inspect.FrameInfo = inspect.stack()[1]

        func: str = stack.function
        file: Path = pathToParents(Path(stack.filename))
        line: int = stack.lineno

        self.root.warning(msg, extra={"func": func, "file": file, "line": line})

    # < ------------------------------------------------------------------- > #

    def error(self, msg: object) -> None:
        stack: inspect.FrameInfo = inspect.stack()[1]

        func: str = stack.function
        file: Path = pathToParents(Path(stack.filename))
        line: int = stack.lineno

        self.root.error(msg, extra={"func": func, "file": file, "line": line})

    # < ------------------------------------------------------------------- > #

    def critical(self, msg: object) -> None:
        stack: inspect.FrameInfo = inspect.stack()[1]

        func: str = stack.function
        file: Path = pathToParents(Path(stack.filename))
        line: int = stack.lineno

        self.root.critical(msg, extra={"func": func, "file": file, "line": line})

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
