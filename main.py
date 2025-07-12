#< pre installed imports >#
from typing import Any
import sys
#< ------------------------ >#

# < photon provided imports >#
try:
    from modules.common import (
        _UNIVERSE, 
        log, 
        projectManifest
    )
except Exception as error:
    print(f"Error: Failed to import module: [main]<-[common]\n {error.args[0].split("(")[0]}")
    sys.exit(1)

try:
    from modules.internals import (
        print_help, 
        print_version, 
        run_package, 
        install_project, 
        uninstall_project, 
        update_project, 
        list_project, 
        refresh_project
    )
except Exception as error:
    print(f"Error: Failed to import module: [main]<-[internals]\n {error.args[0].split("(")[0]}")
    sys.exit(1)
#< ------------------------ >#



#< ------------------------ >#
def main(
        argv:list[Any]=[]
    ) -> None:

    #< [1] would be __file__ >#
    #< [2] should be the start_mode: help, run, etc >#
    #< [3] should be the project name >#
    #< all three a required >#
    if len(argv) < 3:
        log.error("Too few arguments provided")
        print_help("photon")
        sys.exit(1)
    start_mode=argv[1]
    project_name=argv[2]

    valid_photon_arguments=[
        "--log-level"
    ]
    #< default arguments >#
    photon_arguments={
        "log-level": "info"
    }
    project_arguments={}

    #< manifest info >#
    manifest=projectManifest(project_name)

    #< parse args >#
    for_photon=True
    for arg in argv[3:]:
        #< anything after -- is not for photon >#
        if arg == "--":
            for_photon=False
            #< -- shouldn't be added so we skip to next arg >#
            continue

        #< no '=' will make split throw an error >#
        try:
            argument, value=arg.split("=")
        except:
            log.error(f"{arg} lacks a value")
            sys.exit(1)

        #< don't accept blanks >#
        if (argument == "") or (value == ""):
            log.error(f"{arg} lacks a value")
            sys.exit(1)

        if for_photon:
            if argument in valid_photon_arguments:
                #< removing prefiex after checks means user has to use proper -- formatting >#
                argument=argument.removeprefix("-").removeprefix("-")
                photon_arguments[argument]=value
            else:
                log.error(f"{arg} is not a valid option")
                sys.exit(1)
        else:
            #< removing prefiex after checks means user has to use proper -- formatting >#
            argument=argument.removeprefix("-").removeprefix("-")
            project_arguments[argument]=value

    #< info is default >#
    if "log-level" in photon_arguments:
        match photon_arguments["log-level"]:
            case "debug" | "10":
                level=10
            case "trace" | "15":
                level=15
            case "info" | "20":
                level=20
            case "warning" | "30":
                level=30
            case "error" | "40":
                level=40
            case "critical" | "50":
                level=50
            case _:
                log.error("Invalid log-level")
                sys.exit(1)

        for handler in log.handlers:
            handler.setLevel(level)

    #< log setup vars >#
    log.debug(f"OS: {_UNIVERSE.get_os()}")
    log.debug(f"SEPERATOR: {_UNIVERSE.get_seperator()}")
    log.debug(f"ROOT: {_UNIVERSE.get_root()}")

    log.debug(f"ALL_ARGS: {argv}")
    log.debug(f"START_MODE: {start_mode}")

    log.debug(f"PROJECT: {project_name}")
    log.debug(f" -ARGS: {project_arguments}")
    log.debug(f" -MANIFEST: {manifest.exists()}")
    log.debug(f" -INSTALLED: {manifest.installed()}")

    #< no manifest no running, installing, etc >#
    hyperlink=manifest.display_name()
    if manifest.exists():
        project_data=manifest.read()
        try:
            hyperlink="\x1b]8;{};{}\x1b\\{}\x1b]8;;\x1b\\".format("", project_data["project"]["github"], manifest.display_name())
        except KeyError:
            log.warning("No GitHub page provided")
        except Exception as error:
            log.warning(f"Failed to read manifest\n {error}")
    else:
        log.error(f"Unable to {start_mode}, no manifest found for {hyperlink}")
        sys.exit(1)

    #< parse start_mode >#
    if project_name == "photon" and start_mode in ["run", "-r", "install", "-i", "uninstall", "update", "-u"]:
        log.error(f"Invalid start_mode {start_mode} for photon, these are for projects")
        sys.exit(1)

    match start_mode:
        case "help" | "-h":
            log.info(f"Displaying Help Info For: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            print_help(project_name)

        case "version" | "-v":
            log.info(f"Displaying Version Info For: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            print_version(project_name)

        case "run" | "-r":
            log.info(f"Running Project: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            run_package(project_name)

        case "install" | "-i":
            log.info(f"Installing Project: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            install_project(project_name)

        case "uninstall":
            log.info(f"Uninstalling Project: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            uninstall_project(project_name)

        case "update" | "-u":
            log.info(f"Updating Project: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            update_project(project_name)

        case "list" | "-l":
            log.info(f"Listing Project Info For: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            list_project(project_name)

        case "refresh":
            log.info(f"Refreshing Project: {_UNIVERSE.get_colour_style("rich_orange")}{hyperlink}")
            refresh_project(project_name)

        case _:
            log.error("Invalid arguments provided")
            print_help("photon")
            sys.exit(1)
#< ------------------------ >#



#< ------------------------ >#
if __name__ == "__main__":
    main(sys.argv)
#< ------------------------ >#


