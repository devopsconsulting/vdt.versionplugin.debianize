import logging

logging.basicConfig(level=logging.DEBUG)

from apc.versionplugin.debianize.version import get_version
from apc.versionplugin.debianize.package import build_package, set_package_version
