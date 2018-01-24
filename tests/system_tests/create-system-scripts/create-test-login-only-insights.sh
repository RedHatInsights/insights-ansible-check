
NAME=test-login-only-insights

tom-make ${NAME} rhel-7.4 raw --no-register
ansible-playbook -u root -l ${NAME} -e @~/redhat-portal-creds.yml support-playbooks/redhat-insights-registered.yml
ansible-playbook -u root -l ${NAME} tests/system_tests/test-install-ansible-sh.yml

