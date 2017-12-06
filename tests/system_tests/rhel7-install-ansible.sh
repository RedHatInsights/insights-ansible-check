#!/bin/bash

# RHEL7 ansible is in 'extras'
subscription-manager repos --enable=rhel-7-server-extras-rpms
yum install -y ansible


# This isn't needed for ansible,
#    but it is needed for the insights-notify callback plugin
#    this is the easiest place to put it
#yum install -y python-requests
