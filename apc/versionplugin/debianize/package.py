import logging
import subprocess


log = logging.getLogger('apc.versionplugin.debianize.package')


def build_package(version):
    """
    Build package with debianize.
    """
    log.debug("Building version {0} with debianize.".format(version))
    try:
        branch = subprocess.check_output(['git', 'branch'])
        subprocess.check_call(['git', 'checkout', str(version)])
        subprocess.check_call(['debianize.sh', '--version=%s' % version, '--python-install-lib=/usr/lib/python2.7/dist-packages/'])
        subprocess.check_call(['git', 'checkout', branch[2:]])
    except subprocess.CalledProcessError as e:
        log.error("Package creation failed: {0}".format(e))

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
