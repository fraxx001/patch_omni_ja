#!/usr/bin/env sh

BASEDIR=$(dirname "$0")

exec_dir="/usr/local/bin"
hook_dir="/etc/pacman.d/hooks"

exec_bin="$BASEDIR/resources/patch_omni_ja.py"
hook_file="$BASEDIR/resources/firefox.hook"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

if ! hash pacman 2>/dev/null
then
    echo "'pacman' was not found in PATH"
    exit 1
fi


if [ ! -d $exec_dir ] 
then
    mkdir -p $exec_dir
fi

cp $exec_bin $exec_dir

if [ ! -d $hook_dir ] 
then
    mkdir -p $hook_dir
fi

cp $hook_file $hook_dir