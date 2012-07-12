#!/bin/bash

tar -zcf dist.tgz --exclude="*.pyc" --exclude=".svn" --exclude="._*" cvmo/context  templates static
#cat dist.tgz | ssh icharala@lxplus.cern.ch "cat > dist.tgz; echo 'Uploading...'; scp dist.tgz root@cvmappi22.cern.ch:/usr/local/cernvm/"
#cat dist.tgz | ssh -t -t icharala@lxplus.cern.ch "ssh -t -t root@cvmappi22.cern.ch 'cat > /usr/local/cernvm/dist.tgz'; cd /usr/local/cernvm; tar -ztf dist.tgz"
#scp dist.tgz icharala@lxplus.cern.ch:dist.tgz
#ssh -t -t icharala@lxplus.cern.ch "scp -t -t dist.tgz root@cvmappi22.cern.ch:/usr/local/cernvm/"
scp dist.tgz root@cvmappi22.cern.ch:/usr/local/cernvm/
