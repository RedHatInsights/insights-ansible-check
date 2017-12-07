#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2012 Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Copied from the Assert module

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: check
short_description: Checks given expressions are true
description:
     - This module checks that given expressions are true with an optional custom message.
     - This module is also supported for Windows targets.
version_added: "1.5"
options:
  that:
    description:
      - "A string expression of the same form that can be passed to the 'when' statement"
      - "Alternatively, a list of string expressions"
    required: true
  msg:
    description:
      - "The customized message used for a failing check"
notes:
     - This module is also supported for Windows targets.
author:
    - "Ansible Core Team"
    - "Michael DeHaan"
'''

EXAMPLES = '''
- check: { that: "ansible_os_family != 'RedHat'" }

- check:
    that:
      - "'foo' in some_command_result.stdout"
      - "number_of_the_counting == 3"

- check:
    that:
      - "my_param <= 100"
      - "my_param >= 0"
    msg: "'my_param' must be between 0 and 100"
'''
