
NAME=test-login-nothing

tom-make ${NAME} rhel-7.4 raw --no-register
ansible-playbook -u root -l ${NAME} tests/system_tests/test-install-ansible-sh.yml

