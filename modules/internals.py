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
import os
import platform
import sys

from importlib import import_module


# < not pre installed imports ----------------------------------------------------------------- > #
try:
    from prettytable import PrettyTable
except ImportError as error:
    print_import_error(
        import_tree="[internals]<-[prettytable]<-[PrettyTable]",
        error=error,
        link="https://pypi.org/project/prettytable/",
        text="prettytable",
    )


# < photon provided imports ------------------------------------------------------------------- > #
try:
    from modules.common import (
        UNIVERSALS,
        pLOG,
    )
except ImportError as error:
    print_import_error(
        import_tree="[internals]<-[.modules.common]",
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


# < print the [ help | --help | -h ] text for a project taken from its project.yaml file ------ > #
# < d is for default_colour, h is for highlight_colour, r is for reset_colour ----------------- > #
def print_help(project_name: str, argument_manifest: argumentManifest = None) -> None:
    """
    print the [ help | --help | -h ] text for a project taken from its project.yaml file\n
    d is for default_colour, h is for highlight_colour, r is for reset_colour
    """

    if argument_manifest is None:
        argument_manifest = argumentManifest(project_name)

    help_text = argument_manifest.full_help_text()

    # < add colour > #
    help_text = help_text.replace("{d}", UNIVERSALS.styles("default"))
    help_text = help_text.replace("{h}", UNIVERSALS.styles("highlight"))
    help_text = help_text.replace("{r}", UNIVERSALS.styles("reset"))

    print(help_text)


# < print the [ version | --version | -v ] text for a project taken from its project.yaml file  > #
def print_version(
    project_name: str, project_manifest: projectManifest = None, as_table: bool = True
) -> None:
    """
    print the [ version | --version | -v ] text for a project taken from its project.yaml file\n
    if 'as_table' then prettytable is used, otherwise a simple print of the version number
    """

    if project_manifest is None:
        project_manifest = projectManifest(project_name)

    if not as_table:
        print(project_manifest.version())
        return

    table = PrettyTable()
    table.field_names = ["version", "version release date", "version name"]
    table.add_row(
        [
            project_manifest.version(),
            project_manifest.release_date(),
            project_manifest.version_name(),
        ]
    )

    print(f"{UNIVERSALS.styles('cyan')}{table}{UNIVERSALS.styles('reset')}")


# < run a package using importlib.import_module ----------------------------------------------- > #
def run_package(package_name: str) -> None:
    """
    run a package using importlib.import_module
    """

    try:
        import_module(f"packages.{package_name}.main")
    except Exception as error:
        pLOG.error(f"Failed to run package, {error}")


# < run a project using importlib.import_module ----------------------------------------------- > #
def run_project(project_name: str, project_manifest: projectManifest = None) -> None:
    """
    run a project
    """

    if project_manifest is None:
        project_manifest = projectManifest(project_name)

    match project_manifest.project_type():
        case "package":
            run_package(project_name)
        case "script":
            pLOG.error("No Current Implementation")
            # run_script(project_name)
        case "module":
            pLOG.error("No Current Implementation")
            # run_module(project_name)


# < ------------------------------------------------------------------------------------------- > #
def install_project(project_name: str) -> None:
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def uninstall_project(project_name: str) -> None:
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def update_project(project_name: str) -> None:
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def list_project(
    project_name: str,
    project_manifest: projectManifest = None,
    source_manifest: sourceManifest = None,
):
    if project_manifest is None:
        project_manifest = projectManifest(project_name)

    if source_manifest is None:
        source_manifest = sourceManifest(project_name)

    split_left = f"{'':->29}"
    split_right = f"{'':->44}"
    system = platform.system()

    # < the spaces don't change the printed table ------------------------- > #
    # < but they make this more readable ---------------------------------- > #
    table_data = [
        ["name", f"{project_manifest.name()} / {project_manifest.display_name()}"],
        ["summary", project_manifest.summary()],
        ["home page", source_manifest.home_page()],
        [split_left, split_right],
        ["version", project_manifest.version()],
        ["version release date", project_manifest.release_date()],
        ["version name", project_manifest.version_name()],
        [split_left, split_right],
        ["languages", project_manifest.languages()],
        [split_left, split_right],
        ["dependencies", source_manifest.depends()],
        ["recommends", source_manifest.recommends()],
        ["suggests", source_manifest.suggests()],
        [split_left, split_right],
        [f"{system} supported", project_manifest.supported_platform()],
        [f"{system} supported versions", project_manifest.supported_platform_versions()],
    ]

    table = PrettyTable()
    table.field_names = ["Data", "Value"]
    table._min_width = {"Data": 29, "Value": 44}
    table._max_width = {"Data": 29, "Value": 44}
    table.align = "l"
    table.add_rows(table_data)

    d = UNIVERSALS.styles("default")
    r = UNIVERSALS.styles("reset")

    print(f"{d}{table.get_string(header=False)}{r}")


# < ------------------------------------------------------------------------------------------- > #
def refresh_project(project_name: str):
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def dev_init(project_name: str):
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def dev_project_manifest_check(project_name: str):
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def dev_argument_manifest_check(project_name: str):
    pLOG.error("No Current Implementation")


# < ------------------------------------------------------------------------------------------- > #
def dev_source_manifest_check(project_name: str):
    pLOG.error("No Current Implementation")
