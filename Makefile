
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
	install -d /usr/share/insights-policy-check/plugins/action_plugins
	install -d /usr/share/insights-policy-check/plugins/callback_plugins
	install -d /usr/share/insights-policy-check/plugins/library

	install -D --target-directory=/usr/bin bin/insights-policy-check
	install -D --target-directory=/usr/share/insights-policy-check/plugins/action_plugins share/insights-policy-check/plugins/action_plugins/check.py
	install -D --target-directory=/usr/share/insights-policy-check/plugins/callback_plugins share/insights-policy-check/plugins/callback_plugins/notify_insights.py
	install -D --target-directory=/usr/share/insights-policy-check/plugins/library share/insights-policy-check/plugins/library/check.py

uninstall:
	rm -rf /usr/bin/insights-policy-check
	rm -rf /usr/share/insights-policy-check/plugins/action_plugins/check.py
	rm -rf /usr/share/insights-policy-check/plugins/callback_plugins/notify_insights.py
	rm -rf /usr/share/insights-policy-check/plugins/library/check.py
	rm -rf /usr/share/insights-policy-check
