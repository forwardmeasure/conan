#!/bin/bash

export CONAN_USER_HOME=${CONAN_USER_HOME:-/opt/conan}
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

conan export . @forwardmeasure/stable
