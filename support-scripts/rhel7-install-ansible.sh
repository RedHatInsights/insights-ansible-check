#!/bin/bash

# RHEL7 ansible is in 'extras'
subscription-manager repos --enable=rhel-7-server-extras-rpms
yum install -y ansible
