
NAME=test-login-creds-gavin

tom-make ${NAME} rhel-7.4 raw --no-register
ansible-playbook -u root -l ${NAME} tests/system_tests/test-install-ansible-sh.yml
ansible-playbook -u root -l ${NAME} ~/projects/ansible/playbooks/add-user-gavin.yml
ansible-playbook -u root -l ${NAME} ~/projects/ansible/playbooks/enable-sudo-wheel.yml
ansible-playbook -l ${NAME} -e @~/redhat-portal-creds.yml support-playbooks/create-insights-conf.yml

