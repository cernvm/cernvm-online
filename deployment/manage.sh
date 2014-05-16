#!/bin/bash

#
# Launch manage.py with the same server environment.
#

Prefix='/var/www/cernvm-online'

for Lib in lib lib64 ; do
  export PYTHONPATH="${Prefix}/${Lib}/python2.6/site-packages:$PYTHONPATH"
  export LD_LIBRARY_PATH="${Prefix}/${Lib}:$LD_LIBRARY_PATH"
done
export PATH="${Prefix}/bin:$PATH"

if [ "$1" == 'sh' ] ; then
  export PS1='[cvmo-py-env] \w \$> '
  exec bash
else
  exec cvmo-manage "$@"
fi
