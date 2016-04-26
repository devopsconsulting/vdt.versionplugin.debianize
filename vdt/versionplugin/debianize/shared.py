import argparse
import logging
import shutil
import subprocess
import tarfile

from os.path import join, basename, dirname
from glob import glob

from pip.commands.download import DownloadCommand

from vdt.version.utils import empty_directory
from vdt.version.utils import change_directory

log = logging.getLogger(__name__)

pre_remove_script = join(dirname(__file__), 'files/preremove.sh')


class FileFilter(object):
    def __init__(self, include, exclude):
        self.include = include
        self.exclude = exclude

    def __repr__(self):
        return "<FileFilter exclude=%s, include=%s>" % (self.exclude ,self.include)

    def is_filtered(self, path):
        filtered = False
        if self.exclude:
            filtered = any(pattern in path for pattern in self.exclude)
        if self.include:
            filtered = not any(pattern in path for pattern in self.include)

        return filtered


def parse_version_extra_args(version_args):
    p = argparse.ArgumentParser(description="Package python packages with debianize.sh.")
    p.add_argument('--include','-i', action='append', help="Using this flag makes following dependencies explicit. It will only build dependencies listed in install_requires that match the regex specified after -i. Use -i multiple times to specify multiple packages")
    p.add_argument('--exclude', '-I', action='append', help="Using this flag, packages can be exluded from being built, dependencies matching the regex, whill not be built")
    p.add_argument('--maintainer', help="The maintainer of the package", default="nobody@example.com")
    p.add_argument('--pre-remove-script', default=pre_remove_script)
    p.add_argument('--fpm-bin', default='fpm')
    p.add_argument('--python-install-lib', default='/usr/lib/python2.7/dist-packages/')
    p.add_argument('--target', '-t', default='deb', help='the type of package you want to create (deb, rpm, solaris, etc)')
    args, extra_args = p.parse_known_args(version_args)
    
    return args, extra_args


def build_from_python_source_with_fpm(fpm_bin, target, maintainer, pre_remove_script,
        python_install_lib, target_path=None, version=None, *extra_args):
    with change_directory(target_path):
        try:
            cmd = (
                fpm_bin,
                '-s', 'python',
                '-t', target,
                '--maintainer=%s' % maintainer,
                '--exclude=*.pyc',
                '--exclude=*.pyo',
                '--depends=python',
                '--category=python',
                '--before-remove=%s' % pre_remove_script,
                '--template-scripts',
                '--python-install-lib=%s' % python_install_lib
            ) + (tuple() if version is None else ('--version=%s' % version,)) + extra_args + ("setup.py",)
            log.debug("Running command %s" % " ".join(cmd))
            log.debug(subprocess.check_output(cmd))
        except subprocess.CalledProcessError as e:
            log.error("failed to build with fpm status code %s\n%s" % (
                e.returncode, e.output
            ))


class PackageBuilder(object):
    """
    This class build the a package from a python egg, including it's
    dependencies.
    
    It has all kinds of hooks that can be overridden.
    """
    def __init__(self, version, args, extra_args, directory):
        self.version = version
        self.args = args
        self.extra_args = extra_args
        self.directory = directory
        self.exit_code = 0

    def build_package(self, version, args, extra_args):
        # build current directory, which is a python egg
        build_from_python_source_with_fpm(
            args.fpm_bin,
            args.target,
            args.maintainer,
            args.pre_remove_script,
            args.python_install_lib,
            version=version,
            *extra_args
        )

    def download_dependencies(self, install_dir, deb_dir):
        downloader = DownloadCommand(False)
        downloader.main([
                '--no-binary=:all:',
                '--dest=%s' % install_dir,
                deb_dir
        ])
        return glob(join(install_dir, '*.tar.gz'))

    def build_dependency(self, args, extra_args, path, package_dir, deb_dir):
        with tarfile.open(path) as tar:
            tar.extractall(package_dir)
            package_name = basename(path)[:-7]
            target_path = join(package_dir, package_name)
            build_from_python_source_with_fpm(
                args.fpm_bin,
                args.target,
                args.maintainer,
                args.pre_remove_script,
                args.python_install_lib,
                target_path=target_path,
                *extra_args
            )

            for deb in glob(join(target_path, '*.deb')):
                try:
                    shutil.move(deb, deb_dir)
                except shutil.Error:
                    self.exit_code = 5
                    log.error("%s allready exists" % package_name)
        
    def build_dependencies(self, version, args, extra_args, deb_dir):
        # let's download all the dependencies in a temorary directory
        with empty_directory() as install_dir:

            # some packages might not be needed, so construct the filter.
            file_filter = FileFilter(args.include, args.exclude)
            
            # process all the downloaded packages with fpm
            downloaded_packages = self.download_dependencies(install_dir, deb_dir)
            for download in downloaded_packages:
                if file_filter.is_filtered(download):
                    log.info("skipping %s because it is filtered out by %s" % (
                        basename(download), file_filter
                    ))
                else:
                    with empty_directory(install_dir) as package_dir:
                        self.build_dependency(self.args, self.extra_args, download, package_dir, deb_dir)

    def build_package_and_dependencies(self):
        self.build_package(self.version, self.args, self.extra_args)
        self.build_dependencies(self.version, self.args, self.extra_args, self.directory)
