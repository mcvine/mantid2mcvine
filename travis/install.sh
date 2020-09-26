#!/bin/bash
set -e

export GIT_FULL_HASH=`git rev-parse HEAD`
conda config --set always_yes true
conda update conda
conda config --add channels conda-forge
conda config --add channels diffpy
conda config --add channels mantid
conda config --add channels mcvine
conda config --add channels mcvine/label/unstable
conda create -n testenv python=$TRAVIS_PYTHON_VERSION
source activate testenv
conda install pytest pytest-cov coveralls mpich mcvine-core mantid-framework=4
python -c "import matplotlib; import mantid"
mcvine
python setup.py install
