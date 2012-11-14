import subprocess

def build_package(version):
    """
    Build package with debianize.
    """
    subprocess.check_call(['debianize.sh', '--version=%s' % version, '--python-install-lib=/usr/lib/python2.7/dist-packages/'])

def set_package_version(version):
    """
    If there need to be modifications to source files before a
    package can be built (changelog, version written somewhere etc.)
    that code should go here
    """
    if version.annotated and version.changelog and version.changelog != "":
        "modify setup.py and write the version"
        print "got an annotated version, should modify setup.py"
