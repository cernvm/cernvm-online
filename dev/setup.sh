#!/bin/bash
repo_path=$(cd $(dirname $BASH_SOURCE) && cd .. && pwd)

# Python path
new_pp="$repo_path/src"
new_pp+=":$PYTHONPATH"
echo "Setting PYTHONPATH=$new_pp"
export PYTHONPATH=$new_pp

# Binaries path
new_bp="$repo_path/src"
new_bp+=":$PATH"
echo "Setting PATH=$new_bp"
export PATH=$new_bp
