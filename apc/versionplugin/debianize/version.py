"""
This file contains only functions that deal with the version
of the repository. It can set a new version as a tag and look
up the current version.
"""
import subprocess
import logging

from apc.version.shared import VersionNotFound, Version
from apc.versionplugin.default import get_version as get_git_version

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('apc.versionplugin.debianize')


__all__ = ('get_version')


def get_version():
    """
    Retrieve the version from the repo, if no version tag
    can be found, read it from the setup script
    
    It can be assumed that this script will be ran in the
    root of the repository.
    """
    try:
        return get_git_version()
    except VersionNotFound:
        return Version(subprocess.check_output(['python', 'setup.py', '--version']))
