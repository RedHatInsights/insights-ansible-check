
NAME=test-login-rhsm-insights

tom-make ${NAME} rhel-7.4
ansible-playbook -u root -l ${NAME} support-playbooks/redhat-insights-registered.yml
ansible-playbook -u root -l ${NAME} tests/system_tests/test-install-ansible-sh.yml

