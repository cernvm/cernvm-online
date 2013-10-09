#!/bin/bash

#
# Constants
#

GIT_REPO="https://github.com/cernvm/cernvm-online.git"
GIT_BRANCH="master"
BASE_DIR="/var/www/cernvm-online"
SCRIPT_PATH=$(cd $(dirname $BASH_SOURCE) && pwd)
LOG_FILE="$SCRIPT_PATH/log.txt"
rm $LOG_FILE 2> /dev/null # clean files

# Load utilities
source $SCRIPT_PATH/utils.sh

# Steps
declare -a STEPS=("make_dirs export_source prepare_python_env install_mysql install_cmvo configure_cvmo make_public install_apache")
declare -a STEPS_BACKTRACE=()

# Load setup handlers
source $SCRIPT_PATH/setup_handlers.sh

# Main
main

