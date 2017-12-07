# -*- coding: utf-8 -*-
# adapted from the Foreman plugin
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: notify_insights
    type: notification
    short_description: Sends events to Insights
    description:
      - This callback will task events to Insights
    requirements:
'''

from datetime import datetime
from collections import defaultdict
import json
import time
import os
import requests
import ConfigParser
import warnings

from ansible import constants as C
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import stringc

HasSubjectAltNameWarning = False
try:
    from requests.packages.urllib3.exceptions import SubjectAltNameWarning
    HasSubjectAltNameWarning = True
except:
    pass

found_conf_name = 'insights-client'
found_default_conf_dir = os.path.join('/etc', found_conf_name)
for each in ['insights-client', 'redhat-access-insights']:
    if os.path.exists(os.path.join('/etc', each, each + '.conf')):
        found_conf_name = each
        found_default_conf_dir = os.path.join('/etc', each)
        break

possible_CA_VERIFY_files = [
    "/etc/rhsm/ca/redhat-uep.pem",
    "/etc/redhat-access-insights/cert-api.access.redhat.com.pem",
    "/etc/insights-client/cert-api.access.redhat.com.pem",
]

class insights_constants(object):
    app_name = 'insights-request'
    conf_name = found_conf_name
    version = '0.0.1'
    auth_method = 'BASIC'
    log_level = 'DEBUG'
    package_path = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    sleep_time = 300
    user_agent = os.path.join(app_name, 'version')
    default_conf_dir = found_default_conf_dir
    log_dir = os.path.join(os.sep, 'var', 'log', app_name)
    default_log_file = os.path.join(log_dir, app_name) + '.log'
    default_conf_file_name = conf_name + '.conf'
    default_conf_file = os.path.join(default_conf_dir, default_conf_file_name)
    default_sed_file = os.path.join(default_conf_dir, '.exp.sed')
    default_ca_file = "auto" #os.path.join(default_conf_dir, 'cert-api.access.redhat.com.pem')
    base_url = 'cert-api.access.redhat.com/r/insights'
    collection_rules_file = os.path.join(default_conf_dir, '.cache.json')
    collection_fallback_file = os.path.join(default_conf_dir, '.fallback.json')
    collection_remove_file_name = 'remove.conf'
    collection_remove_file = os.path.join(default_conf_dir, collection_remove_file_name)
    unregistered_file = os.path.join(default_conf_dir, '.unregistered')
    registered_file = os.path.join(default_conf_dir, '.registered')
    lastupload_file = os.path.join(default_conf_dir, '.lastupload')
    pub_gpg_path = os.path.join(default_conf_dir, 'redhattools.pub.gpg')
    machine_id_file = os.path.join(default_conf_dir, 'machine-id')
    docker_group_id_file = os.path.join(default_conf_dir, 'docker-group-id')
    default_target = [{'type': 'host', 'name': ''}]
    default_branch_info = {'remote_branch': -1, 'remote_leaf': -1}
    docker_image_name = None
    default_cmd_timeout = 600  # default command execution to ten minutes, prevents long running commands that will hang

class CallbackModule(CallbackBase):
    """
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'notify_insights'

    # Ara doesn't define this at all
    CALLBACK_NEEDS_WHITELIST = False

    TIME_FORMAT = "%Y-%m-%d %H:%M:%S %f"

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.items = defaultdict(list)
        self.insights_system_ids = defaultdict(list)
        self.start_time = int(time.time())

        possible_conf_paths = [
            "/etc/redhat-access-insights/redhat-access-insights.conf",
            "/etc/insights-client/insights-client.conf",
            os.path.expanduser('~/.insights.conf'),
        ]

        path = os.getenv('INSIGHTS_CONF')
        if path:
            possible_conf_paths.append(path)

        self.insights_config = self.parse_config_file(possible_conf_paths)

        self.insights_config_section = None
        for each in ["insights-client", "redhat-access-insights", "redhat_access_insights"]:
            if self.insights_config.has_section(each):
                self.insights_config_section = each
                break

        if self.insights_config_section:
            self.username = self.insights_config.get(self.insights_config_section, "username")
            self.password = self.insights_config.get(self.insights_config_section, "password")
        else:
            self.username = None
            self.password = None

    def parse_config_file(self, conf_file):
        """
        Parse the configuration from the file
        """
        parsedconfig = ConfigParser.RawConfigParser(
            {'loglevel': insights_constants.log_level,
             'trace': 'False',
             'app_name': insights_constants.app_name,
             'auto_config': 'True',
             'authmethod': insights_constants.auth_method,
             'base_url': insights_constants.base_url,
             'upload_url': None,
             'api_url': None,
             'branch_info_url': None,
             'auto_update': 'True',
             'collection_rules_url': None,
             'obfuscate': 'False',
             'obfuscate_hostname': 'False',
             'cert_verify': insights_constants.default_ca_file,
             'gpg': 'True',
             'username': None,
             'password': None,
             'systemid': None,
             'proxy': None,
             'insecure_connection': 'False',
             'no_schedule': 'False',
             'docker_image_name': '',
             'display_name': None})
        try:
            parsedconfig.read(conf_file)
        except ConfigParser.Error:
            self._display.vvv("Could not read configuration file, using defaults")
            pass
        return parsedconfig

    def _build_log(self, data):
        policy_result = {
            "raw_output": "",
            "check_results": []
        }
        for event_name, task_title, result in data:
            if event_name != "skipped":
                policy_result["check_results"].append({
                    "name": task_title,
                    "result": event_name,
                })

        return policy_result

    def send_report(self, host, insights_system_id, policy_result):
        if not self.banner_printed:
            self._display.banner("CHECKMODE SUMMARY")
            self.banner_printed = True
            if not self.username:
                self._display.display("\tNot sending results to Insights, username/password not available")
                self._display.display("")

        # Print out a short summary of the test tasks
        if insights_system_id:
            self._display.display("%s\t\t%s" % (host, insights_system_id))
        else:
            self._display.display("%s" % (host))

        for each in policy_result["check_results"]:
            self._display.display(self._format_summary_for(each))

        if self.username:
            if insights_system_id:
                self._put_report(insights_system_id, policy_result)
            else:
                self._display.display("No system_id for %s" % (host))

        self._display.display("")


    def _format_summary_for(self, task_result):
        if task_result["result"] == "passed":
            icon = stringc("passed", C.COLOR_OK) 
        elif task_result["result"] == "failed":
            icon = stringc("failed", C.COLOR_ERROR)
        elif task_result["result"] == "fatal":
            icon = stringc("ERROR", C.COLOR_ERROR)
        else:
            icon = stringc(task_result["result"], C.COLOR_DEBUG)

        return "    %s : %s"  % (icon, task_result["name"])
    

    def _put_report(self, insights_system_id, policy_result):

        url = "https://cert-api.access.redhat.com/r/insights/v3/systems/%s/policies/%s" % (insights_system_id, self.playbook_name)
        headers = {'Content-Type': 'application/json'}
        verify = False
        for filename in possible_CA_VERIFY_files:
            try:
                with open(filename):
                    verify = filename
                break
            except:
                pass

        self._display.vvv("PUT %s" % url)
        self._display.vvv("VERIFY %s" % verify)
        if HasSubjectAltNameWarning:
            self._display.vvv("Ignoring SubjectAltNameWarning for this PUT")
        else:
            self._display.vvv("Ignoring all warnings for this PUT")
        self._display.vvv(json.dumps(policy_result, indent=2))
        with warnings.catch_warnings():
            if HasSubjectAltNameWarning:
                warnings.simplefilter("ignore", SubjectAltNameWarning)
            else:
                warnings.simplefilter("ignore")
            res = requests.put(url=url,
                               data=json.dumps(policy_result),
                               headers=headers,
                               auth=(self.username, self.password),
                               #cert=cert
                               verify=verify)
        if (res.status_code == 201 or res.status_code == 200) \
           and 'Content-Type' in res.headers and 'json' in res.headers['Content-Type']:
            self._display.vvv("RESULT:")
            self._display.vvv(json.dumps(json.loads(res.content), indent=2))
        else:
            content_type = None
            if 'Content-Type' in res.headers:
                content_type = res.headers['Content-Type']
            self._display.warning('For {}, Unexpected Status Code({}) or Content-Type({}) with content "{}".'.format(url, res.status_code, content_type, res.content))
            if not self.username:
                self._display.warning("Username is empty or None")
            if not self.password:
                self._display.warning("Password is empty or None")

    def send_reports(self):
        self.banner_printed = False
        for host in self.items.keys():
            if host in self.insights_system_ids:
                insights_system_id = self.insights_system_ids[host]
            else:
                insights_system_id = None
            self.send_report(host, insights_system_id, self._build_log(self.items[host]))
            self.items[host] = []

    def append_result(self, result, event_name):
        task_name = result._task.get_name()
        host_name = result._host.get_name()

        if "ansible_facts" in result._result:
            if "ansible_local" in result._result["ansible_facts"]:
                if "insights" in result._result["ansible_facts"]["ansible_local"]:
                    if "system_id" in result._result["ansible_facts"]["ansible_local"]["insights"]:
                        self.insights_system_ids[host_name] = result._result["ansible_facts"]["ansible_local"]["insights"]["system_id"]

        if isinstance(result._task, TaskInclude):
            # probably don't have to treat TaskInclude tasks special for this plugin
            #   but default callback does, so leave this for now
            return

        elif result._task.action == 'setup':
            # we want to remove at least the initial automatic implicit call to the setup module
            # this ignores all calls to setup, implicit or explicit
            # good enough for now
            return

        self._append_result(host_name, event_name, task_name, result._result)

    def _append_result(self, host_name, event_name, task_name, task_result):
        self.items[host_name].append((event_name, task_name, task_result))


    # Ansible Callback API
    #
    #
    #
    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.splitext(os.path.basename(playbook._file_name))[0]

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.append_result(result, "error")

    def v2_runner_on_ok(self, result):
        # This follows the logic of this function in the 'default.py' callback
        # but all we need to determine is "changed" vs "ok"
        # which we translate to "failed" vs "passed"
        if result._result.get('changed', False):
            self.append_result(result, "failed")
        else:
            self.append_result(result, "passed")

    def v2_runner_on_skipped(self, result):
        self.append_result(result, "skipped")

    def v2_runner_on_unreachable(self, result):
        self.append_result(result, "unreachable")

    def v2_playbook_on_stats(self, stats):
        self.send_reports()
