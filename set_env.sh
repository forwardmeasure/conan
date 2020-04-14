#!/bin/bash 

export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

# Load up bootstrapping funcitons
. ${SCRIPTS_DIR}/system_capabilities.sh

# Determine what capabilities we run with
set_env_script

if [[ $? -eq 0 ]]
then
    export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:${MLMA_HOME}:${CONAN_SCRIPT_HOME}

    export LD_LIBRARY_PATH=${MLMA_HOME}/lib:${LD_LIBRARY_PATH}
    export DYLD_LIBRARY_PATH=${MLMA_HOME}/lib:${DYLD_LIBRARY_PATH}
    export PATH=${PATH}:${MLMA_HOME}/bin:${MLMA_HOME}/scripts
else
    echo "FATAL: Unable to set load library path variables correctly"
fi