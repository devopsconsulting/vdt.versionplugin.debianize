from os.path import join, dirname

FILES_PATH = join(dirname(__file__))

PACKAGE_TYPES = {
    'deb': {
        'broken_scheme_names': {
            'pyyaml': 'python-yaml',
            'pyzmq': 'python-zmq',
            'pycrypto': 'python-crypto',
            'python-debian': 'python-debian',
            'python-dateutil': 'python-dateutil'
        },
        'glob': '*.deb'
    },
    'rpm': {
        'broken_scheme_names': {},  # I don't know
        'glob': '*.rpm'
    },
    'osxpkg': {
        'broken_scheme_names': {},  # does not matter
        'glob': '*.pkg'
    }
}


def package_type_choices():
    return PACKAGE_TYPES.keys()
