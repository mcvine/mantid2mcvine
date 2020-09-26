#!/bin/bash

set -e
set -x

conda install -n root conda-build anaconda-client
conda config --set anaconda_upload no

cd travis
sed -e "s|XXXVERSIONXXX|$_CONDA_PKG_VER_|g" meta.yaml.template | sed -e "s|XXXGIT_REVXXX|$GIT_REV|g" > meta.yaml
cat meta.yaml
conda build --python=$TRAVIS_PYTHON_VERSION .
anaconda -t $CONDA_UPLOAD_TOKEN upload --force /home/travis/mc/conda-bld/noarch/mantid2mcvine-$_CONDA_PKG_VER_-*.tar.bz2 --label unstable
