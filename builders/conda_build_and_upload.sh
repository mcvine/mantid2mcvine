#!/bin/bash

GIT_VER=`git describe --tags`
VERSION=`git describe --tags | cut -d '-' -f1 | cut -c2-`
VERSION_NEXT=`echo ${VERSION}| awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}'`
echo ${VERSION} ${VERSION_NEXT}
_CONDA_PKG_VER_=${VERSION_NEXT}.dev
echo conda pkg version:${_CONDA_PKG_VER_}    git version:${GIT_VER}
./travis/create_conda_pkg.sh
