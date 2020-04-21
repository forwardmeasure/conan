#!/bin/bash -x
UNAME=$(tr [A-Z] [a-z] <<< "$(uname)")
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

. ${SCRIPTS_DIR}/functions.sh

CONAN_CHANNEL=@forwardmeasure/stable
LIBS_TO_EXPORT="asio openssl json4moderncpp expat absl protobuf opencv grpc onnx xtl xtensor xtensor-io xframe eigen tensorflow websocketpp cpprestsdk outcome libtorch openblas lapack jemalloc mxnet openexr xgboost boost fmt poco"

while getopts "d:l:i:" opt; do
  case ${opt} in
     d)
      CONAN_FILE_BASE_DIR=$OPTARG
      ;;
     l)
      CONAN_CHANNEL=$OPTARG
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

if [ "x$CONAN_CHANNEL" = "x" ]
then
	echo "Error, you must provide a properly formatted specification for the Conan channel"
	exit 1
fi

if [ "x$LIBS_TO_EXPORT" = "x" ]
then
	echo "Error, you must at least one library to export to Conan"
	exit 1
fi

if [ "x$CONAN_FILE_BASE_DIR" = "x" ]
then
	echo "Error, you must provide the location of the base directory under which the Conan recipe folders reside."
	exit 1
fi

echo -e "Exporting following recipes from recipe directory ${CONAN_FILE_BASE_DIR}:\n${LIBS_TO_EXPORT}"
do_conan_export $CONAN_CHANNEL $CONAN_FILE_BASE_DIR "$LIBS_TO_EXPORT"
