#!/bin/bash
set -e

export GIT_FULL_HASH=`git rev-parse HEAD`
conda config --set always_yes true
conda update conda
conda config --add channels conda-forge
conda config --add channels diffpy
conda config --add channels mantid
conda config --add channels mcvine
conda create -n testenv python=$TRAVIS_PYTHON_VERSION
source activate testenv
#conda install -n testenv numpy 
# conda install mpich
# conda install -c mcvine/label/unstable mantid-framework=3.13 muparser=2.2.5=0
# conda install mantid-framework=4
conda install -c mcvine/label/unstable pytest pytest-cov coveralls mpich mcvine-core mantid-framework=4
python -c "import matplotlib; import mantid"
mcvine
python setup.py install
