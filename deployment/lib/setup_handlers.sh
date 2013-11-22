#!/bin/bash

#
# Step handlers
# each step consists of two methods:
#   * <Step name>_do
#   * <Step name>_undo
#

################################################################################
function make_dirs_do
{
    managed_exec mkdir -p $BASE_DIR
    return $?
}
function make_dirs_undo
{
    managed_exec rm -Rf $BASE_DIR
    return $?
}
################################################################################
function export_source_do
{
    managed_exec yuminst git || return $?

    local SRCSRC=$( cd "$SCRIPT_PATH"/.. ; pwd )
    local SRCDST=$( cd "$BASE_DIR" ; pwd )/src
    if [ "$SRCSRC" != "$SRCDST" ] ; then
        managed_exec ln -nfs "$SRCSRC" "$SRCDST"
    fi
    if [ ! -e "$SRCDST"/.git ] ; then
        managed_exec git clone $GIT_REPO "$BASE_DIR"/src || return $?
    fi
    if [ "$GIT_BRANCH" != '<dont_change_branch>' ] ; then
      ( cd "$BASE_DIR"/src && managed_exec git checkout $GIT_BRANCH )
    fi
    return $?
}
function export_source_undo
{
    managed_exec rm -Rf $BASE_DIR/git || return $?
    managed_exec yum remove git -y
    return $?
}
################################################################################
function prepare_python_env_do
{
    managed_exec yuminst python-pip python-devel gcc
    return $?
}
function prepare_python_env_undo
{
    managed_exec yum remove python-pip python-devel gcc -y
    return $?
}
################################################################################
function install_cvmo_do
{
    # Cleanup pip stuff
    managed_exec rm -rf /tmp/pip-build-root
    # Don't operate in cernvm-online src dir. Clone it somewhere else.
    managed_exec rsync -a --delete --exclude '**/.git' "$BASE_DIR"/src/ "$BASE_DIR"/tmp || return $?
    ( cd "$BASE_DIR"/tmp/src && \
      managed_exec python setup.py sdist ) || return $?
    managed_exec pip install --install-option="--prefix=$BASE_DIR" \
      --upgrade "$BASE_DIR"/tmp/src/dist/CernVM-Online-1.0.tar.gz || return $?
    managed_exec rm -Rf "$BASE_DIR"/tmp || return $?
    managed_exec mkdir -p "$BASE_DIR"/logs
    return $?
}
function install_cvmo_undo
{
    # Cleanup pip stuff
    managed_exec rm -rf /tmp/pip-build-root
    if [ -d $BASE_DIR/git ]; then
        managed_exec rm -Rf $BASE_DIR/git || return $?
    fi
    managed_exec rm -Rf $BASE_DIR/lib || return $?
    managed_exec rm -Rf $BASE_DIR/bin || return $?
    managed_exec rm -Rf $BASE_DIR/logs
    return $?
}
################################################################################
function configure_cvmo_do
{
    managed_exec cp $SCRIPT_PATH/config.py $BASE_DIR/lib/python2.6/site-packages/cvmo/config.py
    return $?
}
function configure_cvmo_undo
{
    managed_exec rm $BASE_DIR/lib/python2.6/site-packages/cvmo/config.py
    return 0
}
################################################################################
function make_public_do
{
    managed_exec mkdir -p "$BASE_DIR"/public_html || return $?
    export PATH="$PATH:$BASE_DIR/bin"
    export PYTHONPATH="$PYTHONPATH:$BASE_DIR/lib/python2.6/site-packages"
    export PYTHONPATH="$PYTHONPATH:$BASE_DIR/lib64/python2.6/site-packages"
    managed_exec $BASE_DIR/bin/manage.py collectstatic --noinput
    return $?
}
function make_public_undo
{
    managed_exec rm -Rf $BASE_DIR/public_html
    return $?
}
################################################################################
function install_mysql_do
{
    managed_exec yuminst mysql-devel || return $?
    managed_exec pip install mysql-python
    return $?
}
function install_mysql_undo
{
    managed_exec yum remove mysql-devel -y || return $?
    managed_exec pip uninstall mysql-python
    return $?
}
################################################################################
function install_apache_do
{
    managed_exec yuminst httpd mod_wsgi mod_ssl || return $?
    managed_exec cp -v "$SCRIPT_PATH"/etc/app.wsgi "$BASE_DIR"/bin/app.wsgi || return $?
    managed_exec cp -v "$SCRIPT_PATH"/etc/cernvm-online.conf /etc/httpd/conf.d/b_cernvm-online.conf || return $?
    if [ -e /etc/httpd/conf.d/wsgi.conf ] ; then
      managed_exec mv /etc/httpd/conf.d/wsgi.conf /etc/httpd/conf.d/a_wsgi.conf || return $?
    fi
    if [ -e /etc/httpd/conf.d/ssl.conf ] ; then
      managed_exec mv /etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/a_ssl.conf || return $?
    fi
    managed_exec chown -R nobody:nobody "$BASE_DIR"/{bin,lib,lib64,public_html} || return $?
    managed_exec chown -R apache:apache "$BASE_DIR"/logs || return $?

    # seLinux fix
    getsebool httpd_can_network_connect 2> /dev/null | \
      grep -q ' --> on$' || \
      managed_exec setsebool -P httpd_can_network_connect on || return $?
  
    #managed_exec /etc/init.d/httpd restart
    return 0 # ignore Apache for the moment...
}
function install_apache_undo
{
    managed_exec yum remove httpd mod_wsgi -y || return $?
    managed_exec setsebool -P httpd_can_network_connect off || return $?
    managed_exec rm -Rf /etc/httpd
    return $?
}
################################################################################
function run_apache_do
{
    managed_exec service httpd stop  # ignore error here
    managed_exec service httpd start || return $?
}
function run_apache_undo
{
    managed_exec service httpd stop # ignore error here
}
################################################################################
