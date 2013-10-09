#!/bin/bash

#
# Step handlers
# each step consists of two methods:
#   * <Step name>_do
#   * <Step name>_undo
#

################################################################################
function checkout_new_do
{
    cd $BASE_DIR
    managed_exec git clone $GIT_REPO git || return $?
    cd git
    managed_exec git checkout $GIT_BRANCH
    return $?
}
function checkout_new_undo
{
    managed_exec rm -Rf $BASE_DIR/git
    return $?
}
################################################################################
function backup_old_do
{
    mkdir $BASE_DIR/backup || return $?
    mv $BASE_DIR/lib/python2.6/site-packages/cvmo $BASE_DIR/backup || return $?
    mv $BASE_DIR/lib/python2.6/site-packages/CernVM* $BASE_DIR/backup
    return $?
}
function backup_old_undo
{
    mv $BASE_DIR/backup/* $BASE_DIR/lib/python2.6/site-packages/ || return $?
    rmdir $BASE_DIR/backup/
    return $?
}
################################################################################
function install_new_do
{
    cd $BASE_DIR/git/src
    managed_exec python setup.py sdist || return $?
    managed_exec pip install --install-option="--prefix=$BASE_DIR" --upgrade dist/CernVM-Online-1.0.tar.gz || return $?
    cd ../../
    managed_exec rm -Rf $BASE_DIR/git || return $?
    return $?
}
function install_new_undo
{
    if [ -d $BASE_DIR/git ]; then
        managed_exec rm -Rf $BASE_DIR/git || return $?
    fi
    managed_exec rm -Rf $BASE_DIR/lib/cvmo || return $?
    managed_exec rm -Rf $BASE_DIR/lib/CernVM*
    return $?
}
################################################################################
function configure_new_do
{
    managed_exec cp $SCRIPT_PATH/config.py $BASE_DIR/lib/python2.6/site-packages/cvmo/config.py
    export PATH="$PATH:$BASE_DIR/bin"
    export PYTHONPATH="$PYTHONPATH:$BASE_DIR/lib/python2.6/site-packages"
    export PYTHONPATH="$PYTHONPATH:$BASE_DIR/lib64/python2.6/site-packages"
    managed_exec mv $BASE_DIR/public_html/static $BASE_DIR/backup || return $?
    managed_exec $BASE_DIR/bin/manage.py collectstatic --noinput
    return $?
}
function configure_new_undo
{
    managed_exec rm $BASE_DIR/lib/python2.6/site-packages/cvmo/config.py
    managed_exec rm -Rf $BASE_DIR/public_html/static || return $?
    managed_exec mv $BASE_DIR/backup/static $BASE_DIR/public_html || return $?
    return 0
}
################################################################################
function restart_apache_do
{
    managed_exec /etc/init.d/httpd restart || return $?
    managed_exec rm -Rf $BASE_DIR/backup
    return $?
}
function restart_apache_undo
{
    return 0
}
################################################################################
