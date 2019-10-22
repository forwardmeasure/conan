#!/bin/bash

export CONAN_USER_HOME=${CONAN_USER_HOME:-/opt/conan}

conan export . @forwardmeasure/stable 
