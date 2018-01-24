#!/bin/bash

# RHEL7 ansible is in 'extras' so use that unless we are not registered
if subscription-manager status; then
    subscription-manager repos --enable=rhel-7-server-extras-rpms
    yum install -y ansible
else
    yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    yum install -y ansible
fi
