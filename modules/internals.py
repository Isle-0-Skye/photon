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
from importlib import import_module
from typing import Any
import os
import sys
#< ------------------------ >#

#< not pre installed imports >#
try:
    from prettytable import PrettyTable
except Exception as error:
    print_import_error(import_tree="[internals]<-[prettytable]<-[PrettyTable]", 
        error=error, 
        link="https://pypi.org/project/prettytable/", text="prettytable")
# < ------------------------ >#

# < photon provided imports >#
try:
    from modules.common import (
        _UNIVERSALS, 
        log, 
        projectManifest
    )
except Exception as error:
    print_import_error("[internals]<-[.modules.common]", 
        error, hypertext=False, import_type="Photon")
#< ------------------------ >#



#< print the [ help | --help | -h ] text for a project taken from its project.yaml file >#
#< d is for default_colour, h is for highlight_colour, r is for reset_colour >#
def print_help(
        project_name:str, 
        project_data:dict[str, Any]=None, # type: ignore
        manifest:projectManifest=None
    ) -> None:
    """
    print the [ help | --help | -h ] text for a project taken from its project.yaml file\n
    if the key: value pair is not set then a warning is logged and the function returns early
    """

    if project_data is None:
        if manifest is None:
            manifest=projectManifest(project_name)
        project_data=manifest.read()

    try:
        help_text=project_data["project"]["help_text"]
    except:
        log.warning("Project has no defined help text")
        return

    help_text=help_text.replace("{d}", _UNIVERSALS.colour_style("cyan"))
    help_text=help_text.replace("{h}", _UNIVERSALS.colour_style("orange"))
    help_text=help_text.replace("{r}", _UNIVERSALS.colour_style("reset"))

    print(help_text)
#< ------------------------ >#



#< print the [ version | --version | -v ] text for a project taken from its project.yaml file >#
def print_version(
        project_name:str, 
        project_data:dict[str, Any]=None, # type: ignore
        manifest:projectManifest=None,
        as_table:bool=True
    ) -> None:
    """
    print the [ version | --version | -v ] text for a project taken from its project.yaml file\n
    if the key: value pair is not set then a warning is logged and the value is set to 'Unknown'\n
    if 'as_table' then prettytable is used, otherwise a simple print of the version number
    """

    if project_data is None:
        if manifest is None:
            manifest=projectManifest(project_name)
        project_data=manifest.read()

    try:
        version_full=project_data["project"]["version"]["full"]
    except:
        log.warning("Failed to read [project][version][full]")
        version_full="Unknown"

    try:
        version_released=project_data["project"]["version"]["released"]
    except:
        log.warning("Failed to read [project][version][released]")
        version_released="Unknown"

    try:
        version_name=project_data["project"]["version"]["name"]
    except:
        log.warning("Failed to read [project][version][name]")
        version_name="Unknown"

    if as_table:
        table_data=[[version_full, version_released, version_name]]
        table_headers=["version", "version release date", "version name"]

        table=PrettyTable()
        table.field_names=table_headers
        table.add_rows(table_data)

        print(f"{_UNIVERSALS.colour_style("cyan")}{table}{_UNIVERSALS.colour_style("reset")}")

    else:
        print(version_full)
#< ------------------------ >#



#< run a package using importlib.import_module >#
def run_package(
        package_name:str
    ) -> None:
    """
    run a package using importlib.import_module
    """

    try:
        import_module(f"packages.{package_name}.main")
    except Exception as error:
        log.error(f"Failed to run package, {error}")
#< ------------------------ >#



#< ------------------------ >#
def install_project(
    project_name:str
    ):
    log.error("No Current Implementation")
    sys.exit(1)
#< ------------------------ >#



#< ------------------------ >#
def uninstall_project(
    project_name:str
    ):
    log.error("No Current Implementation")
    sys.exit(1)
#< ------------------------ >#



#< ------------------------ >#
def update_project(
    project_name:str
    ):
    log.error("No Current Implementation")
    sys.exit(1)
#< ------------------------ >#



#< ------------------------ >#
def list_project(
    project_name:str, 
    project_data:dict[str, Any]=None, # type: ignore
    manifest:projectManifest=None
    ):

    if project_data is None:
        if manifest is None:
            manifest=projectManifest(project_name)
        project_data=manifest.read()

    split_left=f"{"":->29}"
    split_right=f"{"":->44}"

    #< the spaces don't change the printed table, but they make this more readable >#
    table_data=[
        ["name",                        project_data["project"]["name"]],
        ["description",                 project_data["project"]["description"]],
        ["github page",                 project_data["project"]["github"]],
        [split_left, split_right],
        ["version",                     project_data["project"]["version"]["full"]],
        ["version release date",        project_data["project"]["version"]["released"]],
        ["version name",                project_data["project"]["version"]["name"]],
        [split_left, split_right],
        ["languages",                   project_data["project"]["languages"]],
        [split_left, split_right],
        ["dependencies",                project_data["setup"]["requires"]["dependencies"]],
        ["recommends",                  project_data["setup"]["requires"]["recommends"]],
        ["suggests",                    project_data["setup"]["requires"]["suggests"]],
        [split_left, split_right],
        [f"{_UNIVERSALS.os_platform().lower()} support",            project_data["platform"][_UNIVERSALS.os_platform()]["known_supported"]],
        [f"{_UNIVERSALS.os_platform().lower()} supported versions", project_data["platform"][_UNIVERSALS.os_platform()]["version"]["known_supported"]],
        [split_left, split_right],
        ["main programming language",   project_data["language"]["name"]],
        ["intended language version",   project_data["language"]["version"]["full"]],
        ["supported language versions", project_data["language"]["version"]["known_supported"]],
    ]

    table=PrettyTable()
    table.field_names=["Data", "Value"]
    table._min_width={"Data" : 29, "Value" : 44}
    table._max_width={"Data" : 29, "Value" : 44}
    table.align="l"

    table.add_rows(table_data)
    print(f"{_UNIVERSALS.colour_style("log_debug")}{table.get_string(header=False)}{_UNIVERSALS.colour_style("reset")}")
#< ------------------------ >#



#< ------------------------ >#
def refresh_project(
    project_name:str
    ):
    log.error("No Current Implementation")
    sys.exit(1)
#< ------------------------ >#


