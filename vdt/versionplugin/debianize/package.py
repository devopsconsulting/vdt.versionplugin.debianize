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
        cmd = ['debianize.sh'] + includes + ['--version=%s' % version, '--python-install-lib=/usr/lib/python2.7/dist-packages/'] + extra_args
        log.debug("Running command {0}".format(" ".join(cmd)))
        log.debug(subprocess.check_output(cmd))

    return 0


def set_package_version(version):
    """
    If there need to be modifications to source files before a
    package can be built (changelog, version written somewhere etc.)
    that code should go here
    """
    log.debug("set_package_version is not implemented for debianize")
    if version.annotated and version.changelog and version.changelog != "":
        "modify setup.py and write the version"
        log.debug("got an annotated version, should modify setup.py")
