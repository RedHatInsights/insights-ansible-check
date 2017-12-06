#!/bin/bash

# RHEL6 ansible is in EPEL
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
yum install -y ansible

# This isn't needed for ansible,
#    but it is needed for the insights-notify callback plugin
#    this is the easiest place to put it
#yum install -y python-requests

