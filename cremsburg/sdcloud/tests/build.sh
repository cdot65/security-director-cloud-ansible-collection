#!/bin/sh

# ############################################################################
# # Several steps acheived within this script
# #   - Builds our Ansible collection
# #   - Installs our collection
# #   - Executes our Ansible Playbooks in a serial fashion
# ############################################################################
#
# Copyright 2021, Calvin Remsburg
# https://twitter.com/_calvinr
#
# Licensed under the MIT license:
# https://opensource.org/licenses/MIT

ansible-galaxy collection build --force
ansible-galaxy collection install ./cremsburg-sdcloud-0.0.2.tar.gz -p /etc/ansible/collections
cd tests/
ansible-playbook tests.yaml -vvv
