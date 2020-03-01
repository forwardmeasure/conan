#!/bin/bash -x
UNAME=$(tr [A-Z] [a-z] <<< "$(uname)")
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

. ${SCRIPTS_DIR}/functions.sh
. ${SCRIPTS_DIR}/system_capabilities.sh

CONAN_CHANNEL=@forwardmeasure/stable
BUILD_TYPE=Release
CONANFILE_TXT=conanfile.txt
LIBS_TO_EXPORT="openssl json4moderncpp expat abseil protobuf opencv grpc onnx xtl xtensor xtensor-io xframe eigen tensorflow websocketpp cpprestsdk outcome libtorch openblas lapack jemalloc mxnet openexr xgboost boost fmt poco"

while getopts "d:l:i:o:e:c:f:b:l:" opt; do
  case ${opt} in
     o)
      OPTIM_SPEC=$OPTARG
      ;;
     c)
      COMPILER=$OPTARG
      ;;
     e)
      COMPUTE_ENGINE=$OPTARG
      ;;
     b)
      BUILD_TYPE=$OPTARG
      ;;
     l)
      CONAN_CHANNEL=$OPTARG
      ;;
     f)
      CONANFILE_TXT=$OPTARG
      ;;
     d)
      CONAN_FILE_BASE_DIR=$OPTARG
      ;;
     i)
      LIBS_TO_EXPORT=$OPTARG
      ;;
	 \?)
      echo "Invalid option: $OPTARG" 1>&2
	  exit 1
      ;;
     :)
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      ;;
  esac
done
shift $((OPTIND -1))

if ! [[ "$OPTIM_SPEC" =~ ^(all|safe|none)$ ]]
then
	if [ "x$OPTIM_SPEC" = "x" ]
	then
		echo "Warning: defaulting optimisation level to none"
		OPTIM_SPEC="none"
	else
		echo "Error: unknown optimisation level '$OPTIM_SPEC'"
		exit 1
	fi
fi

if ! [[ "$COMPUTE_ENGINE" =~ ^(cpu|cuda_10)$ ]]
then
	if [ "x$COMPUTE_ENGINE" = "x" ]
	then
		echo "Warning: defaulting compute engine type to cpu"
		COMPUTE_ENGINE="cpu"
	else
		echo "Error: unknown compute engine type '$COMPUTE_ENGINE'"
		exit 1
	fi
fi

if [ "x$COMPILER" = "x" ]
then
	get_compiler 'COMPILER'
	echo "Warning: no default compiler specified, defaulting to $COMPILER"
fi

if [ "x$CONAN_FILE_BASE_DIR" = "x" ]
then
    echo "Error, you must provide the location of the base directory under which the Conan recipe folders reside."
    exit 1
fi

ENV_SCRIPT_SPEC=""
compute_env_script_spec 'ENV_SCRIPT_SPEC'
echo "Determined env script spec to be $ENV_SCRIPT_SPEC"

EXTRA_BUILD_SPEC=$(get_env_spec $COMPILER $COMPUTE_ENGINE $OPTIM_SPEC)
BUILD_PROFILE=$UNAME-$EXTRA_BUILD_SPEC
PROFILE_FILE="${SCRIPTS_DIR}/profiles/$BUILD_PROFILE"
INSTALL_FOLDER=${CONAN_USER_HOME}/CMakeModules/${EXTRA_BUILD_SPEC}

# Ensure that Conan uses the new ABI for the default profile
conan profile update settings.compiler.libcxx=libstdc++11 default

# Export the requires recipes
do_conan_export $CONAN_CHANNEL $CONAN_FILE_BASE_DIR "$LIBS_TO_EXPORT"

# Install all packages except TF
do_conan_install $CONANFILE_TXT $CONAN_CHANNEL $BUILD_TYPE $COMPILER $COMPUTE_ENGINE $OPTIM_SPEC $PROFILE_FILE $INSTALL_FOLDER
