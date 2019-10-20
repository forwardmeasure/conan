#!/bin/bash

export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

# pushd ${SCRIPTS_DIR} && python setup.py sdist bdist_wheel && popd
pushd ${SCRIPTS_DIR} && pip install -e . && popd
