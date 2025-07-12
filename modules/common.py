#< pre installed imports >#
from typing import Any
import logging
import os
import platform
import sys
#< ------------------------ >#

#< not pre installed imports >#
try:
    import yaml
except Exception as error:
    hyperlink="\x1b]8;{};{}\x1b\\{}\x1b]8;;\x1b\\".format("", "https://pypi.org/project/PyYAML", "PyYAML")
    print(f"Error: Failed to import module: [common]<-[yaml], is {hyperlink} installed?\n {error}")
    sys.exit(1)
#< ----------------------- >#



#< shared between photon, modules and packages >#
class universals():
    """
    used to share basic data between photon, modules and packages\n
    this contains commonly used information such as project roots
    """

    def __init__(self):
        super().__init__()

        #< what os and seperator >#
        self._OPERATING_SYSTEM=platform.system()

        #< path of this files parent folder >#
        self._ROOT=os.path.realpath(__file__).rsplit(os.sep, 2)[0]

        #< load style file >#
        try:
            with open(os.path.join(self._ROOT, "style.yaml"), "r") as style_file:
                self._STYLES:dict=yaml.safe_load(style_file)
        except:
            print("Error: Failed to read style file, does style.yaml exist?")
            sys.exit(1)

        self._LOG_LEVEL=10
        print("init")

    def get_os(self):
        return self._OPERATING_SYSTEM


    def get_seperator(self):
        return os.sep


    def get_root(self):
        return self._ROOT


    def get_package_root(self, package):
        return os.path.join(self._ROOT, "packages", package)


    def get_colour_style(self, key):
        try:
            return self._STYLES[key]
        except KeyError:
            return ""


    def get_color_style(self, key):
        return self.get_colour_style(key)


    def get_log_level(self):
        return self._LOG_LEVEL

_UNIVERSE=universals()
#< ----------------------- >#



#< formats any logged message using the photon_logger >#
class customFormatter(logging.Formatter):
    """
    formats any logged message using the photon_logger
    """
    message="%(message)s"
    asctime="%(asctime)s"
    levelname="%(levelname)s"
    filename_lineno="%(filename)s:%(lineno)s"

    _ld=_UNIVERSE.get_colour_style("log_debug")
    _li=_UNIVERSE.get_colour_style("log_info")
    _lw=_UNIVERSE.get_colour_style("log_warning")
    _le=_UNIVERSE.get_colour_style("log_error")
    _lc=_UNIVERSE.get_colour_style("log_critical")
    _lr=_UNIVERSE.get_colour_style("reset")

    trace_format=f"{_ld}[{asctime}]{_lr} {_ld}[{levelname}]{_lr} {_ld}[{filename_lineno}]{_lr} {_ld}{message}{_lr}"
    FORMATS = {
        logging.DEBUG:    f"{_ld}[{asctime}]{_lr} {_ld}[{levelname}]{_lr} {_ld}[{filename_lineno}]{_lr} {_ld}{message}{_lr}",
        logging.INFO:     f"{_ld}[{asctime}]{_lr} {_li}[{levelname}]{_lr} {_ld}[{filename_lineno}]{_lr} {_li}{message}{_lr}",
        logging.WARNING:  f"{_ld}[{asctime}]{_lr} {_lw}[{levelname}]{_lr} {_ld}[{filename_lineno}]{_lr} {_lw}{message}{_lr}",
        logging.ERROR:    f"{_ld}[{asctime}]{_lr} {_le}[{levelname}]{_lr} {_ld}[{filename_lineno}]{_lr} {_le}{message}{_lr}",
        logging.CRITICAL: f"{_ld}[{asctime}]{_lr} {_lc}[{levelname}]{_lr} {_ld}[{filename_lineno}]{_lr} {_lc}{message}{_lr}"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)
#< ----------------------- >#



#< courtesy of https://stackoverflow.com/a/35804945 >#
def add_logging_level(
        levelName, 
        levelNum, 
        methodName=None
    ) -> None:
    """
    add a custom logging level to the root logger\n
    slightly modified from https://stackoverflow.com/a/35804945\n
    the only changes are formatting
    """

    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       log.warning(f"{levelName} already defined in logging module")
       return

    if hasattr(logging, methodName):
       log.warning(f"{methodName} already defined in logging module")
       return

    if hasattr(logging.getLoggerClass(), methodName):
       log.warning(f"{methodName} already defined in logger class")
       return

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)

    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, log_for_level)
    setattr(logging, methodName, log_to_root)
#< ----------------------- >#



#< function to import for logging >#
def logger(
        log_level=logging.DEBUG
    ) -> logging.Logger:
    """
    photons logger with a custom 'trace'[15] level between 'debug'[10] and 'info'[20]
    """

    logger = logging.getLogger("photon_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        add_logging_level("TRACE", 15)

    match log_level:
        case "debug":
            log_level=logging.DEBUG
        case "info":
            log_level=logging.INFO
        case "warning":
            log_level=logging.WARNING
        case "error":
            log_level=logging.ERROR
        case "critical":
            log_level=logging.CRITICAL
        case "trace":
            log_level=logging.TRACE

    custom_handler = logging.StreamHandler(sys.stdout)
    custom_handler.setLevel(log_level)

    custom_formatter=customFormatter()
    custom_formatter.FORMATS[logging.TRACE]=custom_formatter.trace_format

    custom_handler.setFormatter(custom_formatter)

    if not logger.handlers:
        logger.addHandler(custom_handler)

    return logger
#< ----------------------- >#



#< setup >#
log=logger(10)
#< ----------------------- >#



#< find info about python >#
def get_python_info(
        info:str
    )-> str | None:
    """
    attempt to find select information about python\n
    if unable to then None is returned

    valid options are:
        exe_name for the filename of sys.executable
        exe_path for sys.executable
    """

    data=None
    match info:
        case "exe_name":
            data=sys.executable.rsplit(_UNIVERSE.get_seperator(), 1)[1]

        case "exe_path":
            data=sys.executable

    return data
#< ----------------------- >#



#< read the project.yaml file for the given project >#
class projectManifest():
    def __init__(
            self, 
            project:str
        ) -> None:

        super().__init__()

        self.original_data=None
        self.old_data=None
        self.new_data=None

        self.manifest_format_version=0
        self.project_name=project
        self.project_display_name=project.replace("_", " ").title()

        if type(project) == str:
            self.project_manifest_path=os.path.join(_UNIVERSE.get_root(), "manifests", "all", f"{project}.yaml")
            self.project_installed_manifest_path=os.path.join(_UNIVERSE.get_root(), "manifests", "installed", f"{project}.yaml")

        self.set_original=True
        self.reload()


    def format_version(
            self
        ) -> int:
        """
        returns the int of the manifest format_version, if unset this returns 0\n
        this value is re-checked during 'reload()'
        """

        return self.manifest_format_version


    def name(
            self
        ) -> str:
        """
        returns the project name used for folders and files, e.g. my_project
        """

        return self.project_name


    def display_name(
            self
        ) -> str:
        """
        returns the project name used for displaying to the user, e.g. My Project\n
        this value is re-checked during 'reload()'
        """

        return self.project_display_name


    def exists(
            self
        ) -> bool:
        """
        returns 'True' if the manifest path exists, else returns 'False'\n
        this value is re-checked during 'reload()'
        """

        return self.manifest_exists


    def installed(
            self
        ) -> bool:
        """
        returns 'True' if the manifest is installed, else returns 'False'\n
        this value is re-checked during 'reload()'
        """

        return self.installed_manifest


    def reload(
            self,
            shift_to_old:bool=True
        ) -> dict[str, Any] | None:
        """
        reload data from the manifest file and shift values then returns the data read from the manifest file and the string 'success'\n
        it this throws an exception then sets a 'None' value for the data\n
        every 'reload()' will update 'exists()', 'installed()' and 'display_name(), 'format_version()'\n
        when data is shifted:\n
        'old_data' will be given the value of 'new_data'\n
        'new_data' will then be given the value of the mainfest file\n
        'original_data' is set on first read and does not change
        """

        if os.path.exists(self.project_manifest_path):
            self.manifest_exists=True
        else:
            self.manifest_exists=False

        if os.path.exists(self.project_installed_manifest_path):
            self.installed_manifest=True
        else:
            self.installed_manifest=False

        try:
            with open(self.project_manifest_path, "r") as project_file:
                self.project_data:dict[str, Any]=yaml.safe_load(project_file)
        except Exception as error:
            log.warning(f"Failed to read project file:\n{error}")
            log.warning("project_data set to None")
            self.project_data=None

        try:
            self.manifest_format_version=self.project_data["format_version"]
        except:
            log.warning("no format_version set")

        try:
            self.project_display_name=self.project_data["project"]["display_name"]
        except:
            log.debug("no display_name set")

        if self.set_original:
            self.original_data=self.project_data
            self.set_original=False

        if shift_to_old:
            self.old_data=self.new_data

        self.new_data=self.project_data

        return self.new_data


    def read(
            self, 
            data:str="new_data", 
            reload_data:bool=False,
            reload_shift_to_old:bool=True
        ) -> dict[str, Any] | None:
        """
        return the chosen data, reloading from the file if 'reload_data' is 'True'\n
        the returned data will be 'None' if an invalid option for 'data' is set\n
        valid 'data' options are 'new_data', 'old_data', 'original_data'\n
        'reload_shift_to_old' is passed to 'reload()', it does nothing if 'reload_data' is 'False'
        """

        if reload_data:
            self.reload(reload_shift_to_old)

        match data:
            case "new_data":
                return self.new_data
            case "old_data":
                return self.old_data
            case "original":
                return self.original_data
            case _:
                log.warning("Invalid data read choice")
                return None
#< ------------------------ >#


