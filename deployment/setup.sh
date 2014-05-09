#!/bin/bash

#
# Constants
#

GIT_REPO="https://github.com/cernvm/cernvm-online.git"

# Set it to the appropriate branch or tag. If set to the special value
# '<dont_change_branch>' it will use the currently selected version
# without performing any 'git checkout'
GIT_BRANCH="<dont_change_branch>"

BASE_DIR="/var/www/cernvm-online"
SCRIPT_PATH=$(cd `dirname "$BASH_SOURCE"` && pwd)
LOG_FILE="$SCRIPT_PATH/log.txt"
rm $LOG_FILE 2> /dev/null # clean files

# Load utilities
source "$SCRIPT_PATH"/lib/utils.sh

# Steps
declare -a STEPS=( make_dirs export_source \
                   prepare_python_env install_mysql \
                   install_cvmo configure_cvmo \
                   make_public install_apache \
                   run_apache )
declare -a QUICK_STEPS=( install_cvmo configure_cvmo make_public run_apache )
declare -a QUICKER_STEPS=( rsync_to_dest configure_cvmo make_public )
declare -a STEPS_BACKTRACE=()

# Parse command-line arguments
for (( I=0 ; I<=$# ; I++ )) ; do

  case "${!I}" in

    -q)  STEPS=( "${QUICK_STEPS[@]}" ) ;;
    -qq) STEPS=( "${QUICKER_STEPS[@]}" ) ;;

  esac

done

# Load setup handlers
source "$SCRIPT_PATH"/lib/setup_handlers.sh

# Main
main
