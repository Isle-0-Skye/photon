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
import os  # noqa: E402
import sys  # noqa: E402

from pathlib import Path  # noqa: E402


# < photon provided imports ------------------------------------------------------------------- > #
try:
    from modules.common import (
        UNIVERSALS,
        pLOG,
        text_to_hypertext,
    )
except ImportError as error:
    print_import_error(
        import_tree="[main]<-[modules.common]",
        error=error,
        hypertext=False,
        import_type="photon",
    )


try:
    from modules.internals import (
        dev_argument_manifest_check,
        dev_init,
        dev_project_manifest_check,
        dev_source_manifest_check,
        install_project,
        list_project,
        print_help,
        print_version,
        refresh_project,
        run_project,
        uninstall_project,
        update_project,
    )
except ImportError as error:
    print_import_error(
        import_tree="[main]<-[modules.internals]",
        error=error,
        hypertext=False,
        import_type="photon",
    )


try:
    from modules.manifests import (
        argumentManifest,
        projectManifest,
        sourceManifest,
    )
except ImportError as error:
    print_import_error(
        import_tree="[main]<-[modules.manifests]",
        error=error,
        hypertext=False,
        import_type="photon",
    )


# < ------------------------------------------------------------------------------------------- > #
def main(argv: list[str] = []) -> None:
    # < [1] would be __file__ --------------------------------------------- > #
    # < [2] should be the start_mode: help, run, etc ---------------------- > #
    # < [3] should be the project name ------------------------------------ > #
    # < all three are required -------------------------------------------- > #
    if len(argv) < 3:
        pLOG.error("too few arguments provided")
        print_help("photon")
        sys.exit(1)
    start_mode = argv[1]
    project_name = argv[2]

    if project_name.startswith("-"):
        pLOG.error(
            f"incorrect formatting, INPUT_2:{project_name} is an argument but should be a project name",
        )
        print_help("photon")
        sys.exit(1)

    if project_name == "photon":
        project_is_photon = True
    else:
        project_is_photon = False

    # < ensure photons manifests exists ------------------------------------------------------- > #
    Path(UNIVERSALS.root(), "manifests", "arguments").mkdir(parents=True, exist_ok=True)
    Path(UNIVERSALS.root(), "manifests", "cached").mkdir(parents=True, exist_ok=True)
    Path(UNIVERSALS.root(), "manifests", "installed").mkdir(parents=True, exist_ok=True)
    Path(UNIVERSALS.root(), "manifests", "sources").mkdir(parents=True, exist_ok=True)

    arguments_manifest_path = Path(UNIVERSALS.root(), "manifests", "arguments", "photon.yaml")
    if not arguments_manifest_path.exists():
        Path.write_text(
            arguments_manifest_path,
            Path.read_text(Path(UNIVERSALS.root(), "vault", "arguments.yaml")),
        )

    cached_manifest_path = Path(UNIVERSALS.root(), "manifests", "cached", "photon.yaml")
    if not cached_manifest_path.exists():
        Path.write_text(
            cached_manifest_path,
            Path.read_text(Path(UNIVERSALS.root(), "vault", "project.yaml")),
        )

    installed_manifest_path = Path(UNIVERSALS.root(), "manifests", "installed", "photon.yaml")
    if not installed_manifest_path.exists():
        Path(UNIVERSALS.root(), "vault", "project.yaml").symlink_to(installed_manifest_path)

    sources_manifest_path = Path(UNIVERSALS.root(), "manifests", "sources", "photon.yaml")
    if not sources_manifest_path.exists():
        Path.write_text(
            sources_manifest_path,
            Path.read_text(Path(UNIVERSALS.root(), "vault", "sources.yaml")),
        )

    # < load photon manifests --------------------------------------------- > #
    hyperlink = text_to_hypertext(" ", "Photon")
    try:
        photon_project_manifest = projectManifest("photon")
    except FileNotFoundError:
        pLOG.warning(f"no project manifest found for: {hyperlink}")
        sys.exit(1)
    except TypeError as error:
        pLOG.warning(f"invalid project manifest found for: {hyperlink} \n  {error}")
        sys.exit(1)

    hyperlink = text_to_hypertext(" ", photon_project_manifest.display_name())
    try:
        photon_source_manifest = sourceManifest("photon")
    except FileNotFoundError:
        pLOG.warning(f"no source manifest found for: {hyperlink}")
        sys.exit(1)
    except TypeError as error:
        pLOG.warning(f"invalid source manifest found for: {hyperlink} \n  {error}")
        sys.exit(1)

    hyperlink = text_to_hypertext(
        photon_source_manifest.home_page(default_value=" "), photon_project_manifest.display_name()
    )
    try:
        photon_argument_manifest = argumentManifest("photon")
    except FileNotFoundError:
        pLOG.warning(f"no argument manifest found for: {hyperlink}")
        sys.exit(1)
    except TypeError as error:
        pLOG.warning(f"invalid argument manifest found for: {hyperlink} \n  {error}")
        sys.exit(1)

    # < load project manifests -------------------------------------------- > #
    hyperlink = text_to_hypertext(" ", project_name)
    try:
        project_source_manifest = sourceManifest(project_name)
    except FileNotFoundError:
        pLOG.warning(f"no source manifest found for: {hyperlink}")
        sys.exit(1)
    except TypeError as error:
        pLOG.warning(f"invalid source manifest found for: {hyperlink} \n  {error}")
        sys.exit(1)

    hyperlink = text_to_hypertext(
        project_source_manifest.home_page(default_value=" "), project_name
    )
    if start_mode not in ["install", "refresh"]:
        try:
            project_argument_manifest = argumentManifest(project_name)
        except FileNotFoundError:
            pLOG.warning(f"no argument manifest found for: {hyperlink}")
            sys.exit(1)
        except TypeError as error:
            pLOG.warning(f"invalid argument manifest found for: {hyperlink} \n  {error}")
            sys.exit(1)

        valid_project_arguments = project_argument_manifest.valid_arguments(with_dash=True)
        project_arguments = project_argument_manifest.default_argument_values()
        valid_project_argument_values = project_argument_manifest.valid_argument_values()

    else:
        valid_project_arguments = []
        project_arguments = {}
        valid_project_argument_values = {}

    # < parse start_mode -------------------------------------------------- > #
    valid_photon_start_modes = photon_argument_manifest.start_modes()
    project_only_modes = [
        "run",
        "-r",
        "install",
        "-i",
        "uninstall",
        "update",
        "-u",
    ]
    photon_only_modes = [
        "dev-init",
        "dev-project-manifest-check",
        "dev-argument-manifest-check",
        "dev-source-manifest-check",
    ]

    if project_is_photon:
        if (start_mode in project_only_modes) or (start_mode not in valid_photon_start_modes):
            pLOG.error(f"invalid start_mode {start_mode} for photon \n  project only mode")
            sys.exit(1)
    else:
        if start_mode in photon_only_modes:
            pLOG.error(f"invalid start_mode {start_mode} for project \n  photon only mode")
            sys.exit(1)

    valid_photon_arguments = photon_argument_manifest.valid_arguments(with_dash=True)
    photon_arguments = photon_argument_manifest.default_argument_values()

    # < split and validate valid arguments -------------------------------- > #
    for_photon = True
    for arg in argv[3:]:
        # < anything after '--' is not for photon ------------------------- > #
        # < '--' shouldn't be added so we skip to next arg ---------------- > #
        if arg == "--":
            for_photon = False
            continue

        # < no '=' will make split throw an error (expects 2, unpacks 1) -- > #
        try:
            argument, value = arg.split("=")
        except ValueError:
            pLOG.error(f"{arg} lacks a value")
            sys.exit(1)

        # < don't accept blanks ------------------------------------------- > #
        if (argument == "") or (value == ""):
            pLOG.error(f"{arg} lacks a value")
            sys.exit(1)

        if (for_photon) and (argument not in valid_photon_arguments):
            pLOG.error(f"{argument} is not a valid option for photon")
            sys.exit(1)

        if (not for_photon) and (argument not in valid_project_arguments):
            pLOG.error(f"{argument} is not a valid option for {project_name}")
            sys.exit(1)

        # < removing prefix after checks means user has to use ------------ > #
        # < proper -- or - formatting ------------------------------------- > #
        # < remove is used twice so this works for long and short options - > #
        # < removeprefix("--") won't work for short hand ------------------ > #
        argument = argument.removeprefix("-").removeprefix("-")

        if for_photon:
            photon_arguments[argument] = value
        else:
            project_arguments[argument] = value

    valid_photon_argument_values = photon_argument_manifest.valid_argument_values()

    # < validate values --------------------------------------------------- > #
    for argument in photon_arguments:
        if photon_arguments[argument] not in valid_photon_argument_values.get(argument, []):
            pLOG.error(f"invalid value: {photon_arguments[argument]}")
            sys.exit(1)

    for argument in project_arguments:
        if project_arguments[argument] not in valid_project_argument_values.get(argument, []):
            pLOG.error(f"invalid value: {project_arguments[argument]}")
            sys.exit(1)

    # < parse photon_arguments -------------------------------------------- > #
    if "log-level" in photon_arguments:
        if photon_arguments["log-level"] not in valid_photon_argument_values.get("log-level", []):
            pLOG.error(f"invalid log level: {photon_arguments['log-level']}")
            sys.exit(1)

        for handler in pLOG.handlers:
            handler.setLevel(photon_arguments["log-level"])

    # < run --------------------------------------------------------------- > #
    if project_is_photon:
        hyperlink = text_to_hypertext(
            photon_source_manifest.home_page(default_value=" "),
            photon_project_manifest.display_name(),
        )
    highlight = UNIVERSALS.styles("rich_orange")

    match start_mode:
        case "help" | "-h":
            pLOG.info(f"displaying help info for:{highlight} {hyperlink}")
            print_help(project_name)

        case "version" | "-v":
            pLOG.info(f"displaying version info for:{highlight} {hyperlink}")
            print_version(project_name)

        case "run" | "-r":
            pLOG.info(f"running project:{highlight} {hyperlink}")
            run_project(project_name)

        case "install" | "-i":
            pLOG.info(f"installing project:{highlight} {hyperlink}")
            install_project(project_name)

        case "uninstall":
            pLOG.info(f"uninstalling project:{highlight} {hyperlink}")
            uninstall_project(project_name)

        case "update" | "-u":
            pLOG.info(f"updating project:{highlight} {hyperlink}")
            update_project(project_name)

        case "list" | "-l":
            pLOG.info(f"listing project info for:{highlight} {hyperlink}")
            list_project(project_name)

        case "refresh":
            pLOG.info(f"refreshing project:{highlight} {hyperlink}")
            refresh_project(project_name)

        # < development options ------------------------------------------- > #
        case "dev-init":
            pLOG.info("dev-mode: init")
            dev_init(project_name)

        case "dev-project-manifest-check":
            pLOG.info("dev-mode: project-manifest-check")
            dev_project_manifest_check(project_name)

        case "dev-argument-manifest-check":
            pLOG.info("dev-mode: argument-manifest-check")
            dev_argument_manifest_check(project_name)

        case "dev-source-manifest-check":
            pLOG.info("dev-mode: source-manifest-check")
            dev_source_manifest_check(project_name)

        case _:
            pLOG.error("Invalid arguments provided")
            print_help("photon")
            sys.exit(1)


# < ------------------------------------------------------------------------------------------- > #
if __name__ == "__main__":
    main(sys.argv)
