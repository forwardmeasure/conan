#!/bin/bash

export CONAN_USER_HOME=${CONAN_USER_HOME:-/opt/bt/conan}
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

CHANNEL=${CHANNEL:-"bottomline/stable"}
INSTALL_DIR=${INSTALL_DIR:-${SCRIPTS_DIR}/CMakeModules}

while getopts ":c:p:i:" opt; do
  case ${opt} in
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

ARTEFACT="asio/1.13.0"
CREATE_OPTIONS=

if [[ ${PROFILE+x} ]]
then
	CONAN_PROFILE_OPTIONS="--profile=${PROFILE_FILE}"
else
	CONAN_PROFILE_OPTIONS=""
fi

conan create --test-folder="None" . "${ARTEFACT}@${CHANNEL}" \
              ${CREATE_OPTIONS}

conan install ${CONAN_PROFILE_OPTIONS} ${SCRIPTS_DIR} --install-folder=${INSTALL_DIR} 
