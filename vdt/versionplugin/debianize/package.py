import logging
import subprocess

from vdt.versionplugin.debianize.shared import parse_version_extra_args

log = logging.getLogger('vdt.versionplugin.debianize.package')


def build_package(version):
    """
    Build package with debianize.
    """
    args, extra_args = parse_version_extra_args(version.extra_args)

    includes = []
    if args.include:
        for include in args.include:
            includes.append('-i')
            includes.append(include)
    
    log.debug("Building version {0} with debianize.".format(version))
    with version.checkout_tag:
        subprocess.check_call(['debianize.sh'] + includes + ['--version=%s' % version, '--python-install-lib=/usr/lib/python2.7/dist-packages/'] + extra_args)
