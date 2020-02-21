#!/bin/bash -x
UNAME=$(tr [A-Z] [a-z] <<< "$(uname)")
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

. ${SCRIPTS_DIR}/functions.sh

CONAN_CHANNEL=@bottomline/stable
LIBS_TO_EXPORT="openssl asio bzip2 cctz abseil boost c-ares gtest poco xtl xtensor xframe onnx protobuf grpc websocketpp cpprestsdk expat apache-apr apache-apr-util apache-log4cxx json4moderncpp xgboost outcome tensorflow"
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

if [ "x$CONAN_FILE_BASE_DIR" = "x" ]
then
	echo "Error, you must provide the location of the base directory under which the Conan recipe folders reside."
	exit 1
fi

do_conan_export $CONAN_CHANNEL $CONAN_FILE_BASE_DIR "$LIBS_TO_EXPORT"
