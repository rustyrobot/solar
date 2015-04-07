import os
import glob

from solar import utils
from solar.extensions.base import BaseExtension
# Import all modules from the directory in order
# to make subclasses for extensions work
modules = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
[__import__(os.path.basename(f)[:-3], locals(), globals()) for f in modules]


def resource(config):
    return playbook.Playbook(config)


def get_all_extensions():
    return BaseExtension.__subclasses__()


def find_extension(id_, version):
    extensions = filter(
        lambda e: e.ID == id_ and e.VERSION == version,
        get_all_extensions())

    if not extensions:
        return None

    return extensions[0]


def find_by_provider_from_profile(profile_path, provider):
    # Circular dependencies problem
    from solar.core import extensions_manager
    from solar.core import profile

    profile = profile.Profile(utils.yaml_load(profile_path))
    extensions = profile.extensions
    result = None
    for ext in extensions:
        result = find_extension(ext['id'], ext['version'])
        if result:
            break

    # Create data manager
    core_manager = extensions_manager.ExtensionsManager(profile)

    return result(profile)