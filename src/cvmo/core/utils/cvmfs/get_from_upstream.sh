#!/bin/bash
cd $( dirname "$0" )
rsync -av --delete --exclude '**/get_from_upstream.sh' ../../../../../extras/cvmfs/python/cvmfs/ ./
