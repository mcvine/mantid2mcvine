#!/bin/bash

set -e
set -x

conda install -n root conda-build
conda install anaconda-client
which anaconda
conda config --set anaconda_upload no

# build
cd travis
sed -e "s|XXXVERSIONXXX|$_CONDA_PKG_VER_|g" meta.yaml.template | sed -e "s|XXXGIT_REVXXX|$GIT_REV|g" > meta.yaml
cat meta.yaml
conda build --python=$TRAVIS_PYTHON_VERSION .

# upload
anaconda -t $CONDA_UPLOAD_TOKEN upload --force /home/travis/mc/conda-bld/noarch/mantid2mcvine-$_CONDA_PKG_VER_-*.tar.bz2 --label unstable
