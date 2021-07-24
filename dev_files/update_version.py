import configparser
from pathlib import Path
from packaging import version


def bump_micro_version(current_version: version.Version) -> version.Version:

    major = current_version.major
    minor = current_version.minor
    micro = current_version.micro

    if micro is None:
        micro = 1
    else:
        micro += 1

    return version.parse(f"{major}.{minor}.{micro}")


def bump_minor_version(current_version: version.Version) -> version.Version:

    major = current_version.major
    minor = current_version.minor
    micro = 0

    if minor is None:
        minor = 1
    else:
        minor += 1

    return version.parse(f"{major}.{minor}.{micro}")


if __name__ == "__main__":

    config_path = Path(__file__).parent.parent / "metadata.txt"

    config = configparser.ConfigParser()

    config.read(str(config_path))

    plugin_version = version.parse(config['general']["version"])

    config['general']["version"] = str(bump_micro_version(plugin_version))

    print(f"Old version: {plugin_version} new version: {config['general']['version']}")

    with open(config_path, "w+") as file_to_save:
        config.write(file_to_save)
