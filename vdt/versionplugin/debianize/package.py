import logging
import subprocess


log = logging.getLogger('vdt.versionplugin.debianize.package')


def build_package(version):
    """
    Build package with debianize.
    """
    log.debug("Building version {0} with debianize.".format(version))
    with version.checkout_tag:
        subprocess.check_call(['debianize.sh', '--version=%s' % version, '--python-install-lib=/usr/lib/python2.7/dist-packages/'] + version.extra_args)

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
