
NAME=test-login-creds-root

tom-make ${NAME} rhel-7.4 raw --no-register
ansible-playbook -u root -l ${NAME} tests/system_tests/test-install-ansible-sh.yml
ansible-playbook -u root -l ${NAME} -e @~/redhat-portal-creds.yml support-playbooks/create-insights-conf.yml

