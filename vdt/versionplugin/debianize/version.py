"""
This file contains only functions that deal with the version
of the repository. It can set a new version as a tag and look
up the current version.
"""
import subprocess
import logging

from vdt.version.shared import VersionNotFound, Version
from vdt.versionplugin.default import get_version as get_git_version

log = logging.getLogger('vdt.versionplugin.debianize.version')


__all__ = ('get_version')


def get_version(version_args):
    """
    Retrieve the version from the repo, if no version tag
    can be found, read it from the setup script
    
    It can be assumed that this script will be ran in the
    root of the repository.
    """
    try:
        return get_git_version(version_args)
    except VersionNotFound:
        log.debug('no version tag found, taking version from setup.py')
        return Version(subprocess.check_output(['python', 'setup.py', '--version']), extra_args=version_args)
