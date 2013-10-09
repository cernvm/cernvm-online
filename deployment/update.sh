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
declare -a STEPS=("checkout_new backup_old install_new configure_new restart_apache")
declare -a STEPS_BACKTRACE=()

# Load update handlers
source $SCRIPT_PATH/update_handlers.sh

# Main
main
