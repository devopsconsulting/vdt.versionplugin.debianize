from os import getcwd
import logging

from vdt.versionplugin.debianize.shared import (
    parse_version_extra_args,
    PackageBuilder
)

log = logging.getLogger('vdt.versionplugin.debianize.package')


def build_package(version):
    """
    Build package with debianize.
    """
    args, extra_args = parse_version_extra_args(version.extra_args)

    log.debug("Building version {0} with debianize.".format(version))
    with version.checkout_tag:
        deb_dir = getcwd()
        # use a package build class which has all kinds of hooks.
        builder = PackageBuilder(version, args, extra_args, deb_dir)
        builder.build_package_and_dependencies()
        return builder.exit_code

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
