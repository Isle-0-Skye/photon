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
import os
import sys
#< ------------------------ >#

# < photon provided imports >#
try:
    from modules.common import (
        _UNIVERSALS, 
        log, 
        projectManifest
    )
except Exception as error:
    print_import_error("[main]<-[.modules.common]", 
        error, hypertext=False, import_type="Photon")

try:
    from modules.internals import (
        install_project, 
        list_project, 
        print_help, 
        print_version, 
        refresh_project,
        run_package, 
        uninstall_project, 
        update_project
    )
except Exception as error:
    print_import_error(import_tree="[main]<-[.modules.internals]", 
            error=error, hypertext=False, import_type="Photon")
#< ------------------------ >#



#< ------------------------ >#
def main(
        argv:list[Any]=[]
    ) -> None:

    #< create the manifest directories and links photons manifest >#
    all_manifests_path=os.path.join(
        _UNIVERSALS.root(), "manifests", "all")

    installed_manifests_path=os.path.join(
        _UNIVERSALS.root(), "manifests", "installed")

    os.makedirs(all_manifests_path, exist_ok=True)
    os.makedirs(installed_manifests_path, exist_ok=True)

    if not os.path.exists (
        os.path.join(all_manifests_path, "photon.yaml")):
        os.symlink(
            os.path.join(_UNIVERSALS.root(), "project.yaml"), 
            os.path.join(all_manifests_path, "photon.yaml")
        )

    if not os.path.exists (
        os.path.join(installed_manifests_path, "photon.yaml")):
        os.symlink(
            os.path.join(_UNIVERSALS.root(), "project.yaml"), 
            os.path.join(installed_manifests_path, "photon.yaml")
        )

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
    log.debug(f"OS: {_UNIVERSALS.os_platform()}")
    log.debug(f"SEPERATOR: {os.sep}")
    log.debug(f"ROOT: {_UNIVERSALS.root()}")

    log.debug(f"ALL_ARGS: {argv}")
    log.debug(f"START_MODE: {start_mode}")

    log.debug(f"PROJECT: {project_name}")
    log.debug(f" -ARGS: {project_arguments}")
    log.debug(f" -MANIFEST: {manifest.exists()}")
    log.debug(f" -INSTALLED: {manifest.installed()}")

    #< no manifest or invalid manifest = no running, installing, etc >#
    hyperlink=manifest.display_name()
    if not manifest.exists():
        log.error(f"Unable to start, no manifest found for {hyperlink}")
        sys.exit(1)

    project_data=manifest.read()
    if project_data is None:
        log.error(f"Unable to start, invalid manifest for {hyperlink}")
        sys.exit(1)

    try:
        hyperlink="\x1b]8;{};{}\x1b\\{}\x1b]8;;\x1b\\".format("", 
            project_data["project"]["github"], manifest.display_name())
    except KeyError:
        log.warning("No GitHub page provided")
    except Exception as error:
        log.warning(f"Failed to read manifest\n {error}")

    #< parse start_mode >#
    project_only_modes=[
        "run", "-r", 
        "install", "-i", 
        "uninstall", 
        "update", "-u"
    ]
    if project_name == "photon" and start_mode in project_only_modes:
        log.error(f"Invalid start_mode {start_mode} for photon")
        sys.exit(1)

    highlight=_UNIVERSALS.colour_style("rich_orange")
    match start_mode:
        case "help" | "-h":
            log.info(f"Displaying Help Info For: {highlight}{hyperlink}")
            print_help(project_name)

        case "version" | "-v":
            log.info(f"Displaying Version Info For: {highlight}{hyperlink}")
            print_version(project_name)

        case "run" | "-r":
            log.info(f"Running Project: {highlight}{hyperlink}")
            run_package(project_name)

        case "install" | "-i":
            log.info(f"Installing Project: {highlight}{hyperlink}")
            install_project(project_name)

        case "uninstall":
            log.info(f"Uninstalling Project: {highlight}{hyperlink}")
            uninstall_project(project_name)

        case "update" | "-u":
            log.info(f"Updating Project: {highlight}{hyperlink}")
            update_project(project_name)

        case "list" | "-l":
            log.info(f"Listing Project Info For: {highlight}{hyperlink}")
            list_project(project_name)

        case "refresh":
            log.info(f"Refreshing Project: {highlight}{hyperlink}")
            refresh_project(project_name)

        #< development options >#
        case "dev-init":
            log.error("Not yet implemented")
            sys.exit(1)

        case "dev-manifest-check":
            log.error("Not yet implemented")
            sys.exit(1)

        case "dev-source-manifest-check":
            log.error("Not yet implemented")
            sys.exit(1)

        case _:
            log.error("Invalid arguments provided")
            print_help("photon")
            sys.exit(1)
#< ------------------------ >#



#< ------------------------ >#
if __name__ == "__main__":
    main(sys.argv)
#< ------------------------ >#


