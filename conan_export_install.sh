#!/bin/bash
UNAME=$(tr [A-Z] [a-z] <<< "$(uname)")
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

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

ARGS=""
if [ "x$CONAN_FILE_BASE_DIR" != "x" ]
then
	ARGS="${ARGS} -d ${CONAN_FILE_BASE_DIR}"
fi

if [ "x$CONAN_CHANNEL" != "x" ]
then
	ARGS="${ARGS} -l ${CONAN_CHANNEL}"
fi

if [ "x$LIBS_TO_EXPORT" != "x" ]
then
	ARGS="${ARGS} -i ${LIBS_TO_EXPORT}"
fi

${SCRIPTS_DIR}/conan_export.sh ${ARGS}
ret=$?

if [[ ${ret} -eq "0" ]]
then
	ARGS=""

	if [ "x$OPTIM_SPEC" != "x" ]
	then
		ARGS="${ARGS} -o ${OPTIM_SPEC}"
	fi

	if [ "x$COMPILER" != "x" ]
	then
		ARGS="${ARGS} -c ${COMPILER}"
	fi

	if [ "x$COMPUTE_ENGINE" != "x" ]
	then
		ARGS="${ARGS} -e ${COMPUTE_ENGINE}"
	fi

	if [ "x$BUILD_TYPE" != "x" ]
	then
		ARGS="${ARGS} -b ${BUILD_TYPE}"
	fi

	if [ "x$CONAN_CHANNEL" != "x" ]
	then
		ARGS="${ARGS} -l ${CONAN_CHANNEL}"
	fi

	if [ "x$CONANFILE_TXT" != "x" ]
	then
		ARGS="${ARGS} -f ${CONANFILE_TXT}"
	fi
	
	${SCRIPTS_DIR}/conan_install.sh ${ARGS}
	ret=$?
fi

exit ${ret}
