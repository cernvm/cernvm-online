#!/bin/bash

# Load echo_*
source /etc/init.d/functions

#
# Helpers
#

function managed_exec
{
    export LAST_LOG_FILE=$(mktemp)
    local RETVAL
    echo ">>> BEGIN OF OPERATION: $@" >> "$LOG_FILE"
    "$@" 2>&1 | tee $LAST_LOG_FILE >> $LOG_FILE
    RETVAL=${PIPESTATUS[0]}
    echo "<<< END($RETVAL) OF OPERATION: $@" >> "$LOG_FILE"
    return $RETVAL
}

function execute_step
{
    local step=$1
    local funct_name=$step"_do"
    eval $funct_name
    return $?
}

function undo_step
{
    local step=$1
    local funct_name="$step\_undo"
    eval $funct_name
    return $?
}

function yuminst
{
    local P INSTALL
    INSTALL=''
    for P in $@ ; do
      rpm -qa | grep "^${P}-" || INSTALL="$INSTALL $P"
    done
    if [ "$INSTALL" != '' ] ; then
      yum install -y $INSTALL
      return $?
    fi
    return 0
}

#
# Controller
#

function main
{
    for step in ${STEPS[@]} ; do
        STEPS_BACKTRACE[${#STEPS_BACKTRACE[@]}]=$step
        echo -n "Executing step $step"
        execute_step $step
        if [ $? -ne 0 ]; then
            echo_failure
            echo
            echo "=== BEGIN LOG ==="
            cat $LAST_LOG_FILE
            echo "=== END LOG ==="
            echo "All logs: $LOG_FILE"

            # Backtrace?
            echo -n 'Do you want to rewind all the changes? Type: "Yes, I do": '
            read ANS
            if [ "$ANS" == 'Yes, I do' ] ; then

                # Run back trace
                echo "Starting back trace..."
                for (( idx=${#STEPS_BACKTRACE[@]}-1 ; idx>=0 ; idx-- )) ; do
                    step=${STEPS_BACKTRACE[idx]}
                    echo -n "Undoing step $step"
                    undo_step $step
                    if [ $? -ne 0 ]; then
                        echo_failure
                    else
                        echo_success
                    fi
                    echo
                done
            else
                echo 'Not undoing changes.'
            fi

            exit 1
        else
            echo_success
            echo
        fi
    done
    exit 0
}
