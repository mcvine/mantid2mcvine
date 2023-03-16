#!/bin/bash

set -e
set -x

conda config --show channels
echo "before installing conda-build"
which conda
conda install -n root conda-build
conda install anaconda-client
which anaconda
conda config --set anaconda_upload no

# build
cd travis
sed -e "s|XXXVERSIONXXX|$_CONDA_PKG_VER_|g" meta.yaml.template | sed -e "s|XXXGIT_REVXXX|${GIT_REV}|g" > meta.yaml
cat meta.yaml
conda build --python=$TRAVIS_PYTHON_VERSION .

# upload
CONDA_ROOT_PREFIX=$(realpath $(dirname `which conda`)/..)
anaconda -t $CONDA_UPLOAD_TOKEN upload --force --label unstable \
         $CONDA_ROOT_PREFIX/conda-bld/noarch/mantid2mcvine-$_CONDA_PKG_VER_-*.tar.bz2
