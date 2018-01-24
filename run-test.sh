#!/bin/bash

NAME=
USER=root

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --user)
            USER=$VALUE
            ;;
        --*)
            echo "ERROR: unknown parameter \"$PARAM\""
            exit 1
            ;;
        *)
            if [ -z "$NAME" ]; then
                NAME=$PARAM
            else
                echo "ERROR: extra parameter \"$PARAM\""
                exit 1
            fi
            ;;
    esac
    shift
done

if [ -z "$NAME" ]; then
    echo "must specify a name for the virtual machine"
    exit 1
fi   

if ! [ -e tests/system_tests/create-system-scripts/create-$NAME.sh ]; then
    echo "no tests/system_tests/create-system-scripts/create-XXX.sh for $NAME"
    exit 1
fi


if ! sudo virsh list --name --all | grep -q $NAME; then
    if ! tests/system_tests/create-system-scripts/create-$NAME.sh; then
        echo >&2 "tests/system_tests/create-system-scripts/create-$NAME.sh failed"
        exit 2
    fi
    sleep 1s
    while ! sudo virsh list --name --state-running | grep -q $NAME; do
        echo "machine not yet running, waiting one second"
        sleep 1s
    done

    tom-reset-networking ${NAME}

elif ! sudo virsh list --name --state-running | grep -q $NAME; then
    if ! sudo virsh start $NAME; then
        echo "machine start command failed"
        exit 1
    fi
    sleep 1s
    while ! sudo virsh list --name --state-running | grep -q $NAME; do
        echo "machine not yet running, waiting one second"
        sleep 1s
    done

    tom-reset-networking ${NAME}
fi
    
ansible-playbook -u "${USER}" -l "${NAME}" -e checkhost=gavin-rhel66-nofips tests/system_tests/test-in-repo.yml
