import configparser
from pathlib import Path
from packaging import version


def bump_dev_version(current_version: version.Version) -> version.Version:

    major = current_version.major
    minor = current_version.minor
    dev = current_version.dev

    if dev is None:
        dev = 1
    else:
        dev += 1

    return version.parse(f"{major}.{minor}.{dev}")


def bump_minor_version(current_version: version.Version) -> version.Version:

    major = current_version.major
    minor = current_version.minor
    dev = 0

    if minor is None:
        minor = 1
    else:
        minor += 1

    return version.parse(f"{major}.{minor}.{dev}")


config_path = Path(__file__).parent.parent / "metadata.txt"

config = configparser.ConfigParser()

config.read(str(config_path))

plugin_version = version.parse(config['general']["version"])

config['general']["version"] = str(bump_dev_version(plugin_version))

with open(config_path, "w+") as file_to_save:
    config.write(file_to_save)
