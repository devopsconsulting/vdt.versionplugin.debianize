"""
This script will be used by fpm to edit the control file during package
building.

The script will correct all the crazy names defined in the ``PACKAGE_TYPES``
configuration object.
"""
import os
import re
import argparse
import tempfile

from vdt.versionplugin.debianize.config import PACKAGE_TYPES, PACKAGE_TYPE_CHOICES


def main():
    p = argparse.ArgumentParser(description="Correct package spec files with weird dependency names.")
    p.add_argument('target',  choices=PACKAGE_TYPE_CHOICES, help="the type of package you want to create (deb, rpm, solaris, etc)")
    p.add_argument('control', help="The path to the control file")

    args = p.parse_args()

    pkgnames = PACKAGE_TYPES[args.target]['broken_scheme_names']
    
    def native_names(match):
        return pkgnames[match.group('pkgname')]
    
    if pkgnames is not None:
        names = "|".join(pkgnames.keys())
        regex = re.compile(r"(?:\bpython-(?P<pkgname>(?:%s))\b)" % names)
        with tempfile.NamedTemporaryFile(delete=False) as out:
            with open(args.control) as inp:
                for line in inp:
                    corrected_line = regex.sub(native_names, line)
                    out.write(corrected_line)
        
        os.rename(out.name, args.control)

if __name__ == '__main__':
    main()
