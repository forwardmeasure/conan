#!/bin/bash

export CONAN_USER_HOME=${CONAN_USER_HOME:-/opt/conan}
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

BUILD_TYPE=${BUILD_TYPE:-Release}

while getopts ":c:b:p:" opt; do
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
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      ;; 
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      ;;
  esac
done
shift $((OPTIND -1))

conan export . @forwardmeasure/stable 
