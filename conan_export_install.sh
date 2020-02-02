#!/bin/bash

export CONAN_USER_HOME=${CONAN_USER_HOME:-/opt/conan}
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"
COMPUTE_ENGINE="cpu"
PROFILE_FILE="${SCRIPTS_DIR}/profiles/$(uname)-install-profile"

while getopts "e:p:" opt; do
  case ${opt} in
     e)
      COMPUTE_ENGINE=$(tr [A-Z] [a-z] <<< "$OPTARG")
      ;;
     p)
      PROFILE_FILE="${SCRIPTS_DIR}/profiles/$OPTARG"
      ;;
     \?)
      echo "Invalid option: $OPTARG" 1>&2
	  exit 1
      ;;
     : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
	  exit 1
      ;;
  esac
done
shift $((OPTIND -1))

conan remote add bintray "https://conan.bintray.com" False --force
conan remote add outcome https://api.bintray.com/conan/ned14/Outcome False --force
conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan False --force

CONAN_CHANNEL=@forwardmeasure/stable
BUILD_TYPE=Release

myName=$(basename $0)
#################################################################################
# We custom export a number of recipes, as there do not exist common ones for them
#################################################################################
LIBS_TO_EXPORT="openssl json4moderncpp expat apache-apr apache-apr-util apache-log4cxx abseil protobuf opencv grpc onnx xtl xtensor xtensor-io xframe eigen tensorflow websocketpp cpprestsdk outcome libtorch openblas lapack jemalloc mxnet openexr xgboost"
for i in ${LIBS_TO_EXPORT}
do
	dir="${SCRIPTS_DIR}/recipes/conan-${i}"
	dirBase="$(basename -- ${dir})"
	if [ -d ${dir} ]
	then
		echo "$myName: Exporting recipe for package $dirBase"
 		conan export ${dir} ${CONAN_CHANNEL}
#		conan create ${dir} ${CONAN_CHANNEL} --keep-source
	else
		echo "Skipping $dirBase"
	fi
done

INSTALL_DIR=${CONAN_USER_HOME}/CMakeModules
mkdir -p ${INSTALL_DIR}

CONAN_BUILD_OPTIONS="--settings build_type=${BUILD_TYPE}"
CONAN_PROFILE_OPTIONS="--profile=${PROFILE_FILE}"
CONAN_INSTALL_OPTIONS="--install-folder=${INSTALL_DIR} ${CONAN_BUILD_OPTIONS} ${CONAN_BUILD_CPP_OPTIONS} --build outdated"

CONANFILE=${SCRIPTS_DIR}/conanfile-${COMPUTE_ENGINE}.txt

#Ensure we are compiling with the CXX11 ABI by default
conan profile update settings.compiler.libcxx=libstdc++11 default

echo "Installing all conan components"
runCmd="conan install ${CONAN_PROFILE_OPTIONS} ${CONAN_INSTALL_OPTIONS} ${CONANFILE}"
echo "Running command ${runCmd}"
eval ${runCmd}
