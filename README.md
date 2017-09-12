vdt.versionplugin.debianize
===========================

Builds system packages from python packages.
Also builds the dependencies of the package.

examples::

    version --plugin=debianize -v --exclude=setuptools
    version --plugin=debianize -v --exclude=setuptools -p
    version --plugin=debianize -v -t rpm --include=django -p
    version --plugin=debianize -v --constraint-file=/path/to/pip/constraint-file.txt

It requires a very specific version of pip.
Because pip changes a lot so it causes a lot of breakage.
