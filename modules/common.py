#< ------------------------ >#
def print_import_error(
        import_tree:str, 
        error:Exception, 
        link:str=None, # type: ignore
        text:str=None, # type: ignore
        import_type:str="Installed",
        hypertext:bool=True
    ):
    print(f"{import_type} Import Error: {import_tree}",
          f"  {error.args[0].split("(")[0]}", sep=os.linesep)
    if hypertext:
        hyperlink=f"\x1b]8;{""};{link}\x1b\\{text}\x1b]8;;\x1b\\"
        print(f"  Is {hyperlink} installed?")
    sys.exit(1)
#< ------------------------ >#

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
    print_import_error(import_tree="[common]<-[yaml]", 
        error=error, link="https://pypi.org/project/PyYAML", text="PyYAML")
#< ------------------------ >#



#< shared between photon, modules and packages >#
class universals():
    """
    used to share basic data between photon, modules and packages\n
    this contains commonly used information such as project roots
    """

    def __init__(
            self
        ) -> None:

        super().__init__()

        #< what os and seperator >#
        self._OPERATING_SYSTEM=platform.system()

        #< path of this files parent directory >#
        self._PHOTON_ROOT=os.path.realpath(__file__).rsplit(os.sep, 2)[0]

        #< load style file >#
        photon_style_file=os.path.join(self._PHOTON_ROOT, "style.yaml")
        if not os.path.exists(photon_style_file):
            print("Error: Failed to read style file, does style.yaml exist?")
            sys.exit(1)

        with open(photon_style_file, "r") as style_file:
            self._STYLES:dict=yaml.safe_load(style_file)

        #< default log level >#
        self._LOG_LEVEL=20


    def os_platform(
            self
        ) -> str:
        """
        returns platform.system()
        """

        return self._OPERATING_SYSTEM


    def root(
            self
        ) -> str:
        """
        returns the directory that contains photons main.py
        """

        return self._PHOTON_ROOT


    def package_root(
            self, 
            package
        ) -> str:
        """
        returns a packages root within photons package directory
        """

        return os.path.join(self._PHOTON_ROOT, "packages", package)


    def installed_manifest_path(
            self,
            project_name:str
        ) -> str|None:
        """
        returns the path to the installed project manifest if it exists\n
        if no installed project manifest if found this returns 'None'
        """

        os.path.join(self._PHOTON_ROOT, 
            "manifests", "installed", f"{project_name}.yaml")


    def installed_manifest_exists(
            self,
            project_name:str
        ) -> bool:
        """
        returns 'True' if an installed project manifest exists\n
        if no installed project manifest if found this returns 'False'
        """

        if self.installed_manifest_path(project_name) is None:
            return False
        else:
            return True


    def all_manifest_path(
            self,
            project_name:str
        ) -> str|None:
        """
        returns the path to the cached project manifest if it exists\n
        if no cached project manifest if found this returns 'None'
        """

        os.path.join(self._PHOTON_ROOT, 
            "manifests", "all", f"{project_name}.yaml")


    def all_manifest_exists(
            self,
            project_name:str
        ) -> bool :
        """
        returns 'True' if a cached project manifest exists else returns\n
        if no cached project manifest if found this returns 'False'
        """

        if self.all_manifest_path(project_name) is None:
            return False
        else:
            return True


    def colour_style(
            self, 
            key
        ):
        """
        returns the relevant escape code for coloured text\n
        there is no different between\n
         'colour_styles()' and 'color_styles()'
        invalid keys return a blank string
        """

        try:
            return self._STYLES[key]
        except KeyError:
            return ""


    def color_style(
            self, 
            key
        ):
        """
        returns the relevant escape code for colored text\n
        there is no different between\n
         'colour_styles()' and 'color_styles()'
        invalid keys return a blank string
        """

        return self.colour_style(key)


    def set_log_level(
            self, 
            level:int
        ) -> None:
        """
        sets the log_level variable \n
        it is up to the project to re-read the value
        """

        self._LOG_LEVEL=level


    def log_level(
            self
        ) -> int:
        """
        returns the value of the current log_level
        """

        return self._LOG_LEVEL


_UNIVERSALS=universals()
#< ------------------------ >#



#< formats any logged message using the photon_logger >#
class customFormatter(logging.Formatter):
    """
    formats any logged message using the photon_logger
    """

    message="%(message)s"
    asctime="%(asctime)s"
    level_name="%(levelname)s"
    file_name_lineno="%(filename)s:%(lineno)s"

    _ld=_UNIVERSALS.colour_style("log_debug")
    _li=_UNIVERSALS.colour_style("log_info")
    _lw=_UNIVERSALS.colour_style("log_warning")
    _le=_UNIVERSALS.colour_style("log_error")
    _lc=_UNIVERSALS.colour_style("log_critical")
    _lr=_UNIVERSALS.colour_style("reset")

    time_fmt=f"{_ld}[{asctime}]{_lr}"
    file_name_lineno_fmt=f"{_ld}[{file_name_lineno}]{_lr}"

    trace_format=f"""
    {time_fmt} {_ld}[{level_name}]{_lr} \
        {file_name_lineno_fmt} {_ld}{message}{_lr}
    """

    FORMATS = {
        logging.DEBUG:    f"{time_fmt} {_ld}[{level_name}]{_lr} \
            {file_name_lineno_fmt} {_ld}{message}{_lr}",

        logging.INFO:     f"{time_fmt} {_li}[{level_name}]{_lr} \
            {file_name_lineno_fmt} {_li}{message}{_lr}",

        logging.WARNING:  f"{time_fmt} {_lw}[{level_name}]{_lr} \
            {file_name_lineno_fmt} {_lw}{message}{_lr}",

        logging.ERROR:    f"{time_fmt} {_le}[{level_name}]{_lr} \
            {file_name_lineno_fmt} {_le}{message}{_lr}",

        logging.CRITICAL: f"{time_fmt} {_lc}[{level_name}]{_lr} \
            {file_name_lineno_fmt} {_lc}{message}{_lr}"
    }


    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)
#< ------------------------ >#



#< courtesy of https://stackoverflow.com/a/35804945 >#
def add_logging_level(
        level_name, 
        level_num, 
        method_name=None
    ) -> None:
    """
    add a custom logging level to the root logger\n
    slightly modified from https://stackoverflow.com/a/35804945
    """

    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
       log.warning(f"{level_name} already defined in logging module")
       return

    if hasattr(logging, method_name):
       log.warning(f"{method_name} already defined in logging module")
       return

    if hasattr(logging.getLoggerClass(), method_name):
       log.warning(f"{method_name} already defined in logger class")
       return


    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)


    logging.addLevelName(level_num, level_name)

    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)
#< ------------------------ >#



#< function to import for logging >#
def logger(
        log_level:int=logging.DEBUG
    ) -> logging.Logger:
    """
    photons logger with a custom 'trace' level of '15' \n
    for context 'debug' is '10' and 'info' is '20'
    """

    logger = logging.getLogger("photon_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        add_logging_level("TRACE", 15)

    custom_handler = logging.StreamHandler(sys.stdout)
    custom_handler.setLevel(log_level)

    custom_formatter=customFormatter()
    custom_formatter.FORMATS[
        logging.TRACE]=custom_formatter.trace_format # type: ignore

    custom_handler.setFormatter(custom_formatter)

    if not logger.handlers:
        logger.addHandler(custom_handler)

    return logger


log=logger(_UNIVERSALS.log_level())
#< ------------------------ >#



#< find info about python >#
def get_python_info(
        info:str
    )-> str|None:
    """
    attempt to find select information about python\n
    if unable to then None is returned

    valid options are:
        exe_name for the filename of sys.executable
        exe_path for sys.executable
    """

    match info:
        case "exe_name":
            data=sys.executable.rsplit(os.sep, 1)[1]

        case "exe_path":
            data=sys.executable

        case _:
            data=None

    return data
#< ------------------------ >#



#< read the project.yaml file for the given project >#
class projectManifest():
    def __init__(
            self, 
            project_name:str
        ) -> None:

        super().__init__()

        self.original_data=None
        self.old_data=None
        self.new_data=None

        self.manifest_format_version=0
        self.project_name=project_name
        self.project_display_name=project_name.replace("_", " ").title()

        self.project_manifest_path=None
        self.project_installed_manifest_path=None

        self.set_original=True
        self.reload()


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

        self.manifest_exists=False
        self.installed_manifest=False

        if _UNIVERSALS.all_manifest_exists(self.project_name):
            self.manifest_exists=True
            self.project_manifest_path=_UNIVERSALS.all_manifest_path(self.project_name)

        if _UNIVERSALS.installed_manifest_exists(self.project_name):
            self.installed_manifest=True
            self.project_installed_manifest_path=_UNIVERSALS.installed_manifest_path(self.project_name)

        try:
            with open(self.project_manifest_path, "r") as project_file: # type: ignore
                self.project_data:dict[str, Any]=yaml.safe_load(project_file)
        except Exception as error:
            log.warning(f"Failed to read project file:\n{error}")
            log.warning("project_data set to None")
            self.project_data=None # type: ignore

        try:
            self.manifest_format_version=self.project_data["format_version"]
        except:
            log.warning("no format_version set")

        try:
            self.project_version=self.project_data["project"]["version"]["full"]
        except:
            log.warning("no version set")

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


    def format_version(
            self
        ) -> int:
        """
        returns the int of the manifest format_version, if unset this returns 0\n
        this value is re-checked during 'reload()'
        """

        return self.manifest_format_version


    def version(
            self
        ) -> str:
        """
        returns the project version as defined in the project file
        """
        return self.project_version


    def name(
            self
        ) -> str:
        """
        returns the project name used for directories and files, e.g. my_project
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


