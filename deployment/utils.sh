#!/bin/bash

# Load echo_*
source /etc/init.d/functions

#
# Helpers
#

function managed_exec
{
    eval "$@" >>$LOG_FILE 2>&1
    return $?
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

#
# Controller
#

function main
{
    for step in $STEPS; do
        STEPS_BACKTRACE+=("$step ")
        echo -n "Executing step $step"
        execute_step $step
        if [ $? -ne 0 ]; then
            echo_failure
            echo

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
            exit 1
        else
            echo_success
            echo
        fi
    done
    exit 0
}
