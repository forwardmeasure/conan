#!/bin/bash -x
UNAME=$(tr [A-Z] [a-z] <<< "$(uname)")
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

. ${SCRIPTS_DIR}/functions.sh
. ${SCRIPTS_DIR}/system_capabilities.sh

CONAN_CHANNEL=@bottomline/stable
BUILD_TYPE=Release
CONANFILE_TXT=conanfile.txt
while getopts "o:e:c:f:b:l:" opt; do
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
		get_optimisation_level 'OPTIM_SPEC'
		echo "Warning: no optimisation level specified, automatically determined to be ${OPTIM_SPEC}"
	else
		echo "Error: unknown optimisation level '$OPTIM_SPEC'"
		exit 1
	fi
fi

if ! [[ "$COMPUTE_ENGINE" =~ ^(cpu|cuda_10)$ ]]
then
	if [ "x$COMPUTE_ENGINE" = "x" ]
	then
		get_compute_engine_type 'COMPUTE_ENGINE'
		echo "Warning: no compute engine specified, automatically determined to be ${COMPUTE_ENGINE}"
	else
		echo "Error: unknown compute engine type '$COMPUTE_ENGINE'"
		exit 1
	fi
fi

if [ "x$COMPILER" = "x" ]
then
	get_compiler 'COMPILER'
	echo "Warning: no compiler specified, automatically determined to be $COMPILER"
fi

if [ "x$CONAN_CHANNEL" = "x" ]
then
    echo "Error, you must provide a properly formatted specification for the Conan channel"
    exit 1
fi

if ! [[ "$BUILD_TYPE" =~ ^(Release|Debug)$ ]]
then
    if [ "x$BUILD_TYPE" = "x" ]
    then
        echo "Warning: defaulting build type to Release"
        BUILD_TYPE="Release"
    else
        echo "Error: unknown build type '$BUILD_TYPE'"
        exit 1
    fi
fi

if [ "x$CONANFILE_TXT" = "x" ]
then
	CONANFILE_TXT=${SCRIPTS_DIR}/conanfile.txt
    echo "Warning: no Conanfile specified, defaulting to $CONANFILE_TXT"
fi

if [ ! -f "$CONANFILE_TXT" ]
then
    echo "File ${CONANFILE_TXT} does not exist"
	exit 1
fi


EXTRA_BUILD_SPEC=$(get_extra_build_spec $COMPILER $COMPUTE_ENGINE $OPTIM_SPEC)
BUILD_PROFILE=$UNAME-$EXTRA_BUILD_SPEC
PROFILE_FILE="${SCRIPTS_DIR}/profiles/$BUILD_PROFILE"
INSTALL_FOLDER=${CONAN_USER_HOME}/CMakeModules/${EXTRA_BUILD_SPEC}

# Ensure that Conan uses the new ABI for the default profile
#conan profile update settings.compiler.libcxx=libstdc++11 default
#conan profile update settings.compiler.libcxx=libstdc++11 ${BUILD_PROFILE}

do_conan_install $CONANFILE_TXT $CONAN_CHANNEL $BUILD_TYPE $COMPILER $COMPUTE_ENGINE $OPTIM_SPEC $PROFILE_FILE $INSTALL_FOLDER
