#!/bin/bash

#
# Constants
#

GIT_REPO="https://github.com/cernvm/cernvm-online.git"
#GIT_BRANCH="master"
GIT_BRANCH="<dont_change_branch>"
BASE_DIR="/var/www/cernvm-online"
SCRIPT_PATH=$(cd `dirname "$BASH_SOURCE"` && pwd)
LOG_FILE="$SCRIPT_PATH/log.txt"
rm $LOG_FILE 2> /dev/null # clean files

# Load utilities
source $SCRIPT_PATH/utils.sh

# Steps
declare -a STEPS=( make_dirs export_source \
                   prepare_python_env install_mysql \
                   install_cvmo configure_cvmo \
                   make_public install_apache \
                   run_apache )
declare -a QUICK_STEPS=( install_cvmo configure_cvmo run_apache )
declare -a STEPS_BACKTRACE=()

# Parse command-line arguments
for (( I=0 ; I<=$# ; I++ )) ; do
  if [ "${!I}" == '-q' ] || [ "${!I}" == '--quick' ] ; then
    STEPS=( "${QUICK_STEPS[@]}" )
  fi
done

# Load setup handlers
source $SCRIPT_PATH/setup_handlers.sh

# Main
main

