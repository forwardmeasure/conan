#!/bin/bash

export CONAN_USER_HOME=${CONAN_USER_HOME:-/opt/bt/conan}
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

BUILD_TYPE=${BUILD_TYPE:-Release}
CHANNEL=${CHANNEL:-"forwardmeasure/stable"}
INSTALL_DIR=${INSTALL_DIR:-${SCRIPTS_DIR}/CMakeModules}

while getopts ":b:c:p:i:" opt; do
  case ${opt} in
    b )
      BUILD_TYPE=$OPTARG
      ;;
    c )
      CHANNEL=$OPTARG
      ;;
    p )
      PROFILE=$OPTARG
      ;;
    i )
      INSTALL_DIR=$OPTARG
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      ;; 
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      ;;
  esac
done
shift $((OPTIND -1))

ARTEFACT="expat/2.2.6"
CREATE_OPTIONS="--options shared=True"

if [[ ${PROFILE+x} ]]
then
	CONAN_PROFILE_OPTIONS="--profile=${PROFILE_FILE}"
else
	CONAN_PROFILE_OPTIONS=""
fi

conan create --test-folder="None" . "${ARTEFACT}@${CHANNEL}" \
             --settings build_type=${BUILD_TYPE} ${CREATE_OPTIONS}

conan install ${CONAN_PROFILE_OPTIONS} ${SCRIPTS_DIR} --install-folder=${INSTALL_DIR} \
              --generator=cmake --generator=cmake_multi --generator=cmake_paths --generator=pkg_config \
              --generator=compiler_args --generator=gcc --generator=virtualrunenv \
              --settings build_type=${BUILD_TYPE} ${CREATE_OPTIONS}
