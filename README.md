CernVM Online
=============

This repository contains the source code for
[CernVM Online](https://cernvm-online.cern.ch/).
CernVM Online is based on the Python [Django](https://www.djangoproject.com/)
framework.

Deployment
----------

This section briefly describes what to do to get the software installed on a
(virtual) machine running Apache and WSGI. Switching between different branches
has been made easier through a setup/update script.

### Step 1. Create a new RHEL6-based VM

Instructions and deployment script have been tested on SLC 6 only, but can be
easily adapted to any OS with little effort.

### Step 2. Obtain the software

Clone the Git repository somewhere:

    git clone https://github.com/cernvm/cernvm-online.git /root/cvmo.git

Choose the branch/tag you want:

    cd /root/cvmo.git
    git checkout <your_branch_name>

### Step 3. Configure

You must provide a `config.py` configuration file in the `deployment`
subdirectory of your Git clone:

    cp /your/path/config.py /root/cvmo.git/deployment/config.py

*You can get an example configuration file from the production host.*

**Beware!** The file shall not be committed since it contains sensitive
information (credentials, etc.)!

Additional configuration (like the installation path) can be performed by
editing the setup file:

    $YOUR_EDITOR /root/cvmo.git/deployment/setup.sh

but you mostly not need to touch it.

### Step 4. Run the setup script

Run the automatic deployment script **as root**:

    /root/cvmo.git/deployment/setup.sh

Installation of additional components and configuration of Apache and the WSGI
interface will be performed automatically. The web server will be restarted at
the end.

### Step 5. Updates

Updates on the Git repository are meant to be maintained manually. In general,
synchronizing a branch means roughly:

    cd /root/cvmo.git
    git checkout <your_branch_name>
    git pull

The repository does not contain the production files. Changed files must be
deployed by running again the setup script:

    /root/cvmo.git/deployment/setup.sh [-qq|-q]

The `-q` parameter runs a minimal number of operations to put in production the
new files and takes much less time than the full process. The `-qq` switch
makes the operation even faster.

**Note:** the "quick" switches should be used in development only. Use the full
setup with no switches when promoting to production.

**Enjoy!**
