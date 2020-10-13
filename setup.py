#!/usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
version_ns = {}
with open(os.path.join(here, 'mantid2mcvine', '_version.py')) as f:
    exec(f.read(), {}, version_ns)

# define distribution
setup(
    name = "mantid2mcvine",
    version = version_ns['__version__'],
    packages = find_packages(".", exclude=['tests', 'notebooks', 'demo']),
    # package_dir = {'': "."}, # this seems to be no good for including data files
    # this is replaced by MANIFEST.in
    # data_files = [('mantid2mcvine/nxs', ['mantid2mcvine/nxs/start.nxs'])],
    test_suite = 'tests',
    install_requires = [
    ],
    dependency_links = [
    ],
    author = "MCViNE team",
    description = "Convert Mantid instrument IDF to MCViNE",
    license = 'BSD',
    keywords = "instrument, neutron",
    url = "https://github.com/mcvine/mantid2mcvine",
    include_package_data = True,
    # download_url = '',
)

# End of file
