
default:
	@echo "This will install insights-policy-check onto this system"
	@echo
	@echo "   sudo make install"
	@echo " or"
	@echo "   sudo make uninstall"

install:
	# this first part is for an older version of install (on RHEL6) which does not
	# support -D --target-directory=...
	install -d /usr/bin
	install -d /usr/share/ansible/plugins/action
	install -d /usr/share/ansible/plugins/modules
	install -d /usr/share/ansible/plugins/callback

	install -D --target-directory=/usr/bin bin/insights-policy-check
	install -D --target-directory=/usr/share/ansible/plugins/action share/insights-policy-check/plugins/action_plugins/check.py
	install -D --target-directory=/usr/share/ansible/plugins/modules share/insights-policy-check/plugins/library/check.py
	install -D --target-directory=/usr/share/ansible/plugins/callback share/insights-policy-check/plugins/callback_plugins/notify_insights.py 


uninstall:
	rm -rf /usr/bin/insights-policy-check
	rm -rf /usr/share/ansible/plugins/action/check.py
	rm -rf /usr/share/ansible/plugins/modules/check.py
	rm -rf /usr/share/ansible/plugins/callback/notify_insights.py

