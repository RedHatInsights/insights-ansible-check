
NAME=test-login-rhsm-only

tom-make ${NAME} rhel-7.4
ansible-playbook -u root -l ${NAME} tests/system_tests/test-install-ansible-sh.yml

