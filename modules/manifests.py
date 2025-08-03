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

from pathlib import Path
from typing import Any


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

# < photon provided imports ------------------------------------------------------------------- > #
try:
    from modules.common import (
        UNIVERSALS,
    )
except ImportError as error:
    print_import_error(
        import_tree="[manifests]<-[modules.common]",
        error=error,
        hypertext=False,
        import_type="photon",
    )


# < manifest class for common functionality between its subclasses ---------------------------- > #
class Manifest:
    def __init__(self, project_name: str, manifest_directory: str) -> None:
        self.project_name = project_name
        self.manifest_filepath = Path(
            UNIVERSALS.root(), "manifests", manifest_directory, f"{self.project_name}.yaml"
        )
        self.manifest_data = self.read_file_data()

    def exists(self) -> bool:
        """
        returns true if the manifest filepath exists otherwise returns false
        """
        return self.manifest_filepath.exists()

    def installed(self) -> bool:
        """
        returns true if the project is installed, else returns false
        """

        return Path(
            UNIVERSALS.root(), "manifests", "installed", f"{self.project_name}.yaml"
        ).exists()

    def get_data(self) -> dict[str, Any]:
        """
        returns the dict of the currently stored manifest data\n
        this is the data that other methods use rather than re-reading the file
        """

        return self.manifest_data

    def set_data(self, data: dict[str, Any]) -> None:
        """
        sets the dict of the currently stored manifest data\n
        this is the data that other methods use rather than re-reading the file
        """

        self.manifest_data = data

    def read_file_data(self) -> dict[str, Any]:
        """
        returns a dict of all the data read from the manifest file\n
        if the file does not exist a FileNotFoundError is raised\n
        if the data is not a dict, implying an invalid manifest, a TypeError is raised
        """

        if self.manifest_filepath.exists():
            with open(self.manifest_filepath, "r") as manifest_file:
                manifest_data = yaml.safe_load(manifest_file)

            data_type = type(manifest_data)
            if data_type is dict:
                return manifest_data

            raise TypeError(f"manifest is a {data_type} but should be a dict")

        raise FileNotFoundError(self.manifest_filepath)

    def reload_if_valid(self) -> bool:
        """
        returns true if able to set the stored manifest data to the manifest file data\n
        this set will fail if the file data is not a dict and return false
        """

        # just in case
        data = self.get_data()
        try:
            self.set_data(self.read_file_data())
            return True
        except TypeError or FileNotFoundError:
            self.set_data(data)
            return False

    def format_version(self, default_value: int | None = None) -> int | None:
        """
        returns the format version data from the manifest\n
        if the data does not exist default_value is returned
        """

        return self.get_data().get("format_version", default_value)


# < ------------------------------------------------------------------------------------------- > #
class projectManifest(Manifest):
    def __init__(self, project_name) -> None:
        super().__init__(project_name, "cached")

    def project_type(self) -> str:
        """
        returns the project type
        """

        return self.get_data().get("project", {}).get("type", {})

    def name(self) -> str:
        """
        returns the project name used for directories and files, e.g. my_project
        """

        return self.get_data().get("project", {}).get("name", {})

    def display_name(self) -> str:
        """
        returns the project name used for displaying to the user, e.g. My Project
        """

        return self.get_data().get("project", {}).get("display_name", {})

    def summary(self) -> str:
        """
        returns the project summary
        """

        return self.get_data().get("project", {}).get("summary", {})

    def version(self) -> str:
        """
        returns the project version
        """

        return self.get_data().get("project", {}).get("version", {}).get("full", {})

    def release_date(self) -> str:
        """
        returns the project version release date
        """

        return self.get_data().get("project", {}).get("version", {}).get("released", {})

    def version_name(self) -> str:
        """
        returns the project version name
        """

        return self.get_data().get("project", {}).get("version", {}).get("name", {})

    def languages(self) -> list[str]:
        """
        returns the projects supported languages
        """

        return self.get_data().get("project", {}).get("languages", {})

    def supported_platforms(self) -> list[str]:
        """
        returns a list of the projects supported platforms
        """

        supported = []

        for platform_name, platform_data in self.get_data().get("platform", {}).items():
            if platform_data.get("known_supported", False):
                supported.append(platform_name)

        return supported

    def supported_platform_versions(self) -> list[str]:
        """
        returns the projects supported platform versions
        """

        return (
            self.get_data()
            .get("platform", {})
            .get(platform.system(), {})
            .get("version", {})
            .get("known_supported", {})
        )

    def supported_platform(self) -> bool:
        """
        returns true if the current platform is known to be supported
        """

        if (platform.system() in self.supported_platforms()) and (
            platform.release().rsplit(".", 1)[0] in self.supported_platform_versions()
        ):
            return True
        else:
            return False


# < read the sources.yaml file for the given project ------------------------------------------ > #
class sourceManifest(Manifest):
    def __init__(self, project_name) -> None:
        super().__init__(project_name, "sources")

    def home_page(self, version: str = "latest", default_value: str | None = None) -> str:
        """
        returns a str of the projects home page\n
        if no data is found default_value is used
        """

        return self.get_data().get(version, {}).get("home_page", default_value)

    def depends(self, version: str = "latest", default_value: list[str] | None = None) -> list[str]:
        """
        returns a list of required software to have installed\n
        if no data is found default_value is used
        """

        return self.get_data().get(version, {}).get("depends", default_value)

    def recommends(
        self, version: str = "latest", default_value: list[str] | None = None
    ) -> list[str]:
        """
        returns a list of recommended software to have installed\n
        if no data is found default_value is used
        """

        return self.get_data().get(version, {}).get("recommends", default_value)

    def suggests(
        self, version: str = "latest", default_value: list[str] | None = None
    ) -> list[str]:
        """
        returns a list of suggested software to have installed\n
        if no data is found default_value is used
        """

        return self.get_data().get(version, {}).get("suggests", default_value)


# < read the arguments.yaml file for the given project ---------------------------------------- > #
class argumentManifest(Manifest):
    def __init__(self, project_name) -> None:
        super().__init__(project_name, "arguments")

    def help_text(self, default_value: str | None = None) -> str:
        """
        returns the help text data from the argument manifest\n
        if the data does not exist default_value is returned
        """

        return self.get_data().get("help_text", default_value)

    def full_help_text(self):
        """
        returns the help text as well as any start modes or additional arguments
        """

        # < {d} is default colour ----------------------------------------- > #
        # < {h} is highlight colour --------------------------------------- > #
        # < {r} is reset colour ------------------------------------------- > #

        data = f"{{d}}{self.help_text()}"

        # < start modes --------------------------------------------------- > #
        if len(self.start_modes()) > 0:
            data = "\n".join([data, "\n{h}start_mode options:{r}"])

        for mode in self.start_modes():
            mode_data = self.start_mode(mode)

            argument = f"  {{h}}{mode} | {mode_data.get('short_hand')}:{{r}}"
            description = f"    {{d}}desc: {mode_data.get('description')}{{r}}"

            data = "\n".join([data, argument, description])

        # < optional arguments -------------------------------------------- > #
        if len(self.optional_arguments()) > 0:
            data = "\n".join([data, "\n{h}optional_argument options:{r}"])

        for optional_arg in self.optional_arguments():
            optional_arg_data = self.optional_argument(optional_arg)

            argument = f"  {{h}}{optional_arg} | {optional_arg_data.get('short_hand')}:{{r}}"
            description = f"    {{d}}desc: {optional_arg_data.get('description')}{{r}}"
            values = f"    {{d}}values: {optional_arg_data.get('valid_values')}{{r}}"
            default = f"    {{d}}default: {optional_arg_data.get('default_value')}{{r}}"

            data = "\n".join([data, argument, description, values, default])

        # < exclusive arguments ------------------------------------------- > #
        if len(self.exclusive_arguments()) > 0:
            data = "\n".join([data, "\n{h}exclusive_argument options:{r}"])

        for exclusive_arg in self.exclusive_arguments():
            exclusive_arg_data = self.exclusive_argument(exclusive_arg)

            argument = f"  {{h}}{exclusive_arg} | {exclusive_arg_data.get('short_hand')}:{{r}}"
            description = f"    {{d}}desc: {exclusive_arg_data.get('description')}{{r}}"
            values = f"    {{d}}values: {optional_arg_data.get('valid_values')}{{r}}"
            default = f"    {{d}}default: {optional_arg_data.get('default_value')}{{r}}"

            data = "\n".join([data, argument, description, values, default])

        return "".join([data, "{r}"])

    def start_modes(self) -> list[str]:
        """
        returns a list of names of start modes
        """

        return list(self.get_data().get("start_modes", {}).keys())

    def start_mode(self, mode: str, default_value: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        returns a dict of the data for the specified start mode\n
        if the data does not exist default_value is returned
        """

        start_modes_dict = self.get_data().get("start_modes", {})
        return start_modes_dict.get(mode, default_value)

    def optional_arguments(self) -> list[str]:
        """
        returns a list of names of optional arguments
        """

        return list(self.get_data().get("optional_arguments", {}).keys())

    def optional_argument(
        self, argument: str, default_value: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        returns a dict of the data for the specified optional argument\n
        if the data does not exist default_value is used
        """

        optional_arguments_dict = self.get_data().get("optional_arguments", {})
        return optional_arguments_dict.get(argument, default_value)

    def exclusive_arguments(self) -> list[str]:
        """
        returns a list of names of exclusive arguments
        """

        return list(self.get_data().get("exclusive_arguments", {}).keys())

    def exclusive_argument(
        self, argument: str, default_value: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        returns a dict of the data for the specified exclusive argument\n
        if the data does not exist default_value is used
        """

        exclusive_arguments_dict = self.get_data().get("exclusive_arguments", {})
        return exclusive_arguments_dict.get(argument, default_value)

    def default_argument_values(self, default_value: str | None = None) -> dict[str, str]:
        """
        returns a dict of default argument values for any optional arguments\n
        if no default value is found then default_value is used
        """

        data = {}

        for argument, value in self.get_data().get("optional_arguments", {}).items():
            data[argument] = value.get("default_value", default_value)

        return data

    def valid_arguments(self, with_dash: bool = False) -> list[str]:
        """
        returns a list of names of valid arguments for both optional and exclusive arguments\n
        if with_dash is true a double dash '--' will be added to the start of each argument
        """

        data = []

        data.extend(self.optional_arguments())
        data.extend(self.exclusive_arguments())

        if not with_dash:
            return data

        data = ["--" + argument for argument in data]

        return data

    def valid_argument_values(self, default_value: list[str] | None = None) -> dict[str, list[str]]:
        """
        returns a dict of valid values for any valid arguments\n
        if no valid value data is found then default_value is used
        """

        data = {}

        for argument, value in self.get_data().get("optional_arguments", {}).items():
            data[argument] = value.get("valid_values", default_value)

        for argument, value in self.get_data().get("exclusive_arguments", {}).items():
            data[argument] = value.get("valid_values", default_value)

        return data
