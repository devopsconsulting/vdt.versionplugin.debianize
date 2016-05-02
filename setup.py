# coding: utf-8
from setuptools import find_packages, setup

pkgname = "vdt.versionplugin.debianize"

setup(name=pkgname,
      version="1.0.2",
      description="Version Increment Plugin that builds with debianize",
      author="Lars van de Kerkhof",
      author_email="lars@permanentmarkers.nl",
      maintainer="Lars van de Kerkhof",
      maintainer_email="lars@permanentmarkers.nl",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['vdt', 'vdt.versionplugin'],
      zip_safe=True,
      install_requires=[
          "setuptools",
          "vdt.version>=0.1.4",
          "vdt.versionplugin.default",
          "pip==8.1.1"
      ],
      entry_points={
        'console_scripts':[
            'vdt.fpmeditor = vdt.versionplugin.debianize.fpmeditor:main',
        ]
      },
)
