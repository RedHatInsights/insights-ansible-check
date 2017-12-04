
default:
	@echo "This will install insights-ansible-check onto this system"
	@echo
	@echo "   sudo make install"
	@echo " or"
	@echo "   sudo make uninstall"

install:
	# this first part is for an older version of install (on RHEL6) which does not
	# support -D --target-directory=...
	install -d /usr/bin
	install -d /usr/share/insights-ansible-check/plugins/action_plugins
	install -d /usr/share/insights-ansible-check/plugins/callback_plugins
	install -d /usr/share/insights-ansible-check/plugins/library

	install -D --target-directory=/usr/bin bin/insights-ansible-check
	install -D --target-directory=/usr/share/insights-ansible-check/plugins/action_plugins share/insights-ansible-check/plugins/action_plugins/check.py
	install -D --target-directory=/usr/share/insights-ansible-check/plugins/callback_plugins share/insights-ansible-check/plugins/callback_plugins/notify_insights.py
	install -D --target-directory=/usr/share/insights-ansible-check/plugins/library share/insights-ansible-check/plugins/library/check.py

uninstall:
	rm -rf /usr/bin/insights-ansible-check
	rm -rf /usr/share/insights-ansible-check/plugins/action_plugins/check.py
	rm -rf /usr/share/insights-ansible-check/plugins/callback_plugins/notify_insights.py
	rm -rf /usr/share/insights-ansible-check/plugins/library/check.py
	rm -rf /usr/share/insights-ansible-check
