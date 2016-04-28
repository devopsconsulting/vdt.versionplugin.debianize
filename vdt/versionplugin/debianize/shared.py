import argparse
import logging
import os
import re
import shutil
import subprocess
import tarfile
import zipfile

from os.path import join, basename
from glob import glob

from pip.commands.download import DownloadCommand

from vdt.version.utils import empty_directory
from vdt.version.utils import change_directory

from vdt.versionplugin.debianize.config import PACKAGE_TYPES, PACKAGE_TYPE_CHOICES, FILES_PATH

log = logging.getLogger(__name__)

pre_remove_script = join(FILES_PATH, 'files/preremove.sh')

PACKAGE_NAME_REGEX = re.compile(r"(?P<name>.*)-.*")


class FileFilter(object):
    def __init__(self, include, exclude):
        self.include = include
        self.exclude = exclude

    def __repr__(self):
        return "<FileFilter exclude=%s, include=%s>" % (self.exclude ,self.include)

    def is_filtered(self, path):
        filtered = False
        if self.exclude:
            filtered = any(re.search(pattern, basename(path), re.IGNORECASE) is not None for pattern in self.exclude)
        if self.include:
            filtered = not any(re.search(pattern, basename(path), re.IGNORECASE) is not None for pattern in self.include)

        return filtered


class DebianizeArgumentParser(object):
    "Package python packages with debianize.sh."
    def __init__(self, version_args):
        self.version_args = version_args

    def get_parser(self):
        p = argparse.ArgumentParser(description=self.__doc__)
        p.add_argument('--include','-i', action='append', help="Using this flag makes following dependencies explicit. It will only build dependencies listed in install_requires that match the regex specified after -i. Use -i multiple times to specify multiple packages")
        p.add_argument('--exclude', '-I', action='append', help="Using this flag, packages can be exluded from being built, dependencies matching the regex, whill not be built")
        p.add_argument('--maintainer', help="The maintainer of the package", default="nobody@example.com")
        p.add_argument('--pre-remove-script', default=pre_remove_script)
        p.add_argument('--fpm-bin', default='fpm')
        p.add_argument('--python-install-lib', default='/usr/lib/python2.7/dist-packages/')
        p.add_argument('--target', '-t', default='deb', choices=PACKAGE_TYPE_CHOICES, help='the type of package you want to create (deb, rpm, solaris, etc)')
        p.add_argument('--no-python-dependencies', default=False, action='store_true', help="Do not include requirements defined in setup.py as dependencies.")
        p.add_argument('--vdt-fpmeditor-path', default='vdt.fpmeditor', help="path to vdt.fpmeditor or some other script you need to use on package spec files.")
        return p

    def parse_known_args(self):
        p = self.get_parser()
        args, extra_args = p.parse_known_args(self.version_args)
    
        return args, extra_args


def parse_version_extra_args(version_args):
    parser = DebianizeArgumentParser(version_args)
    return parser.parse_known_args()


def build_from_python_source_with_fpm(args, extra_args, target_path=None, version=None, file_name=None):
    with change_directory(target_path):
        try:
            cmd = [
                args.fpm_bin,
                '-s', 'python',
                '-t', args.target,
                '--maintainer=%s' % args.maintainer,
                '--exclude=*.pyc',
                '--exclude=*.pyo',
                '--depends=python',
                '--category=python',
                '--before-remove=%s' % args.pre_remove_script,
                '--template-scripts',
                '--python-install-lib=%s' % args.python_install_lib
            ]
            if version is not None:
                cmd.append('--version=%s' % version)
            if args.no_python_dependencies:
                cmd.append('--no-python-dependencies')
            cmd += extra_args

            config = PACKAGE_TYPES[args.target]
            broken_scheme_names = config['broken_scheme_names']

            # some packages have weird names that need fixing.
            # they need fixing on 2 places, the package name itself and also
            # everywhere where dependencies are declared.
            if broken_scheme_names is not None:
                if file_name is not None:
                    package_name = PACKAGE_NAME_REGEX.match(file_name).group('name')
                    if package_name in broken_scheme_names:  # package name is broken, override package name
                        cmd += ['--name', broken_scheme_names[package_name]]

                # make sure that control file is passed to vdt.fpmeditor
                # for correction of weird dependency names.
                env = os.environ.copy()
                env['EDITOR'] = "%s %s" % (args.vdt_fpmeditor_path, args.target)

                cmd.append('-e')
                cmd.append("setup.py")

                log.debug("Running command %s with scheme name filter" % " ".join(cmd))
                log.debug(subprocess.check_output(cmd, env=env))
            else:
                cmd.append("setup.py")
                log.debug("Running command %s" % " ".join(cmd))
                log.debug(subprocess.check_output(cmd))

            return 0
        except subprocess.CalledProcessError as e:
            log.error("failed to build with fpm status code %s\n%s" % (
                e.returncode, e.output
            ))
            return 1


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
        # some packages might not be needed, so construct the filter.
        self.file_filter = FileFilter(args.include, args.exclude)

    def update_exit_code(self, code):
        if self.exit_code == 0:
            self.exit_code = code

    def build_package(self, version, args, extra_args):
        # build current directory, which is a python egg
        ex = build_from_python_source_with_fpm(
            args,
            extra_args,
            version=version
        )
        self.update_exit_code(ex)

    def download_dependencies(self, install_dir, deb_dir):
        downloader = DownloadCommand(False)
        downloader.main([
                '--no-binary=:all:',
                '--dest=%s' % install_dir,
                deb_dir
        ])
        return glob(join(install_dir, '*.tar.gz')) + glob(join(install_dir, '*.zip'))

    def select_file_type(self, path):
        if path.lower().endswith('.zip'):
            return zipfile.ZipFile(path), basename(path)[:-4]
        else:  # assume it is a tarball
            return tarfile.open(path), basename(path)[:-7]

    def build_dependency(self, args, extra_args, path, package_dir, deb_dir):
        handle, package_name = self.select_file_type(path)
        with handle as tar:  # extract the python package
            tar.extractall(package_dir)

            # determine folder name where setup.py lives
            target_path = join(package_dir, package_name)
            ex = build_from_python_source_with_fpm(
                args,
                extra_args,
                target_path=target_path,
                file_name=package_name
            )
            self.update_exit_code(ex)

            # moves debs to common folder.
            for deb in glob(join(target_path, PACKAGE_TYPES[args.target]['glob'])):
                try:
                    shutil.move(deb, deb_dir)
                except shutil.Error:
                    self.update_exit_code(5)
                    log.error("%s allready exists" % package_name)

    def build_dependencies(self, version, args, extra_args, deb_dir):
        # let's download all the dependencies in a temorary directory
        with empty_directory() as install_dir:

            # process all the downloaded packages with fpm
            downloaded_packages = self.download_dependencies(install_dir, deb_dir)
            for download in downloaded_packages:
                if self.file_filter.is_filtered(download):
                    log.info("skipping %s because it is filtered out by %s" % (
                        basename(download), self.file_filter
                    ))
                else:
                    with empty_directory(install_dir) as package_dir:
                        self.build_dependency(self.args, self.extra_args, download, package_dir, deb_dir)

    def build_package_and_dependencies(self):
        self.build_package(self.version, self.args, self.extra_args)
        if not self.args.no_python_dependencies:
            self.build_dependencies(self.version, self.args, self.extra_args, self.directory)
