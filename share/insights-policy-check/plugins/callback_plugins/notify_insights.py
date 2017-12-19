# -*- coding: utf-8 -*-
# adapted from the Foreman plugin
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: notify_insights
    type: notification
    short_description: Treat task results as PASS/FAIL and sends results to Insights as a Policy
    description:
      - Treat task results as PASS/FAIL and sends results to Insights as a Policy
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

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'notify_insights'

    # Ara doesn't define this at all
    CALLBACK_NEEDS_WHITELIST = False

    TIME_FORMAT = "%Y-%m-%d %H:%M:%S %f"

    def v3(self, message):
        self._display.vvv("[notify_insights plugin] " + message)

    def warning(self, message):
        self._display.warning("[notify_insights plugin] " + message)

    def error(self, message):
        self._display.error("[notify_insights plugin] " + message)

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

        possible_conf_sections = [
            "insights-client",
            "redhat-access-insights",
            "redhat_access_insights",
        ]

        path = os.getenv('INSIGHTS_CONF')
        if path:
            possible_conf_paths.append(path)

        self.insights_config = self.parse_config_file(possible_conf_paths)

        self.v3("Searching for Insights config sections from: %s" % possible_conf_sections)
        self.insights_config_section = None
        for each in possible_conf_sections:
            if self.insights_config.has_section(each):
                self.insights_config_section = each
                break
        self.v3("Using Insights config section: %s" % self.insights_config_section)

        username = None
        password = None
        cert = None

        if self.insights_config_section:
            username = self.insights_config.get(self.insights_config_section, "username")
            password = self.insights_config.get(self.insights_config_section, "password")

        if username:
            self.v3("Found 'username' in configuration, using BASIC AUTH to login to Insights")
            if password == None:
                password = ""
                self.warning("Found NO 'password' in configuration, using BASIC AUTH with empty password")
        else:
            self.v3("Not using BASIC AUTH to login to Insights, could not find 'username' in configuration")
            try:
                from rhsm.config import initConfig
                rhsm_config = initConfig()
                rhsm_consumerCertDir = rhsm_config.get('rhsm', 'consumerCertDir')

                cert_filename = os.path.join(rhsm_consumerCertDir, "cert.pem")
                rhsm_key_filename = os.path.join(rhsm_consumerCertDir, "key.pem")

                def try_open(file, file_kind):
                    try:
                        self.v3("Found %s: %s" % (file_kind, file))
                        open(file).close()
                    except Exception as ex:
                        self.v3("Could not open %s %s: %s" % (file_kind, file, ex))
                        raise ex

                try_open(cert_filename, "RHSM CERT")
                try_open(rhsm_key_filename, "RHSM KEY")

                cert = (cert_filename, rhsm_key_filename)

            except Exception as ex:
                self.v3("Not using CERT AUTH to login to Insights, could not load RHSM CERT or KEY: %s" % ex)

        self.session = None
        if username or cert:
            self.v3("Setting up HTTP Session")
            self.session = requests.Session()
            self.session.auth = (username, password)
            self.session.cert = cert

            possible_CA_VERIFY_files = [
                "/etc/rhsm/ca/redhat-uep.pem",
                "/etc/redhat-access-insights/cert-api.access.redhat.com.pem",
                "/etc/insights-client/cert-api.access.redhat.com.pem",
            ]

            self.session.verify = False
            for filename in possible_CA_VERIFY_files:
                try:
                    with open(filename):
                        self.session.verify = filename
                        break
                except:
                    pass
            self.v3("HTTP Session VERIFY %s" % self.session.verify)

            self.session.headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'notify_insights',
                'Accept': 'application/json',
            }


    def parse_config_file(self, conf_file):
        """
        Parse the configuration from the file
        """

        self.v3("Searching for Insights config files at: %s" % conf_file)

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
            self.v3("Could not read configuration file, using defaults")
            pass
        return parsedconfig

    def _build_log(self, data):
        policy_result = {
            "raw_output": "",
            "check_results": []
        }
        for task_result_summary, task_title, task_result_full in data:
            if task_result_summary != "skipped":
                policy_result["check_results"].append({
                    "name": task_title,
                    "result": task_result_summary,
                })

        return policy_result

    def send_report(self, host, insights_system_id, policy_result):
        if not self.banner_printed:
            self._display.banner("CHECKMODE SUMMARY")
            self.banner_printed = True
            if not self.session:
                self._display.display("\tNot sending results to Insights, not registered and username/password not available")
                self._display.display("")

        # Print out a short summary of the test tasks
        if insights_system_id:
            self._display.display("%s\t\t%s" % (host, insights_system_id))
        else:
            self._display.display("%s" % (host))

        for each in policy_result["check_results"]:
            self._display.display(self._format_summary_for(each))

        if self.session:
            if insights_system_id:
                self._put_report(insights_system_id, policy_result)
            else:
                self._display.display("No system_id for %s" % (host))

        self._display.display("")


    def _format_summary_for(self, check_result):
        if check_result["result"] == "pass":
            icon = stringc("pass", C.COLOR_OK)
        elif check_result["result"] == "fail":
            icon = stringc("fail", C.COLOR_ERROR)
        elif check_result["result"] == "fatal":
            icon = stringc("ERROR", C.COLOR_ERROR)
        else:
            icon = stringc(check_result["result"], C.COLOR_DEBUG)

        return "    %s : %s"  % (icon, check_result["name"])


    def _put_report(self, insights_system_id, policy_result):

        url = "https://cert-api.access.redhat.com/r/insights/v3/systems/%s/policies/%s" % (insights_system_id, self.playbook_name)

        self.v3("PUT %s" % url)
        if HasSubjectAltNameWarning:
            self.v3("Ignoring SubjectAltNameWarning for this PUT")
        else:
            self.v3("Ignoring all warnings for this PUT")
        self.v3("REQUEST Content: " + json.dumps(policy_result, indent=2))
        with warnings.catch_warnings():
            if HasSubjectAltNameWarning:
                warnings.simplefilter("ignore", SubjectAltNameWarning)
            else:
                warnings.simplefilter("ignore")
            res = self.session.put(url=url, data=json.dumps(policy_result))

        def format_response(display_function, response):
            display_function("RESPONSE Status Code: %s" % response.status_code)
            display_function("RESPONSE Reason: %s" % response.reason)

            try:
                # Insights normally returns JSON
                display_function("RESPONSE Content: %s" % json.dumps(response.json(), indent=2))

            except:
                # Just in case
                if 'Content-Type' in response.headers:
                    display_function("RESPONSE Content-Type: %s" % response.headers['Content-Type'])
                else:
                    display_function("RESPONSE Content-Type: None")
                display_function("RESPONSE Content: %s" % response.text)

        if res.status_code in (200,201):
            format_response(self.v3, res)

        elif res.status_code == 401:
            if self.session.auth:
                self.error("Username/Password not valid for Insights")
            if self.session.cert:
                self.error("Certificate not valid for Insights")
            if not (self.session.auth or self.session.cert):
                self.error("Authorization Required for Insights")
            format_response(self.error, res)

        else:
            self.error("Unexpected Response")
            format_response(self.error, res)

    def send_reports(self):
        self.banner_printed = False
        for host in self.items.keys():
            if host in self.insights_system_ids:
                insights_system_id = self.insights_system_ids[host]
            else:
                insights_system_id = None
            self.send_report(host, insights_system_id, self._build_log(self.items[host]))
            self.items[host] = []

    def append_result(self, result, event_type):
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

        self._append_result(host_name,
                            event_type,
                            task_name,
                            result._result)

    def _append_result(self, host_name, event_type, task_name, task_result):
        self.items[host_name].append((self.summarize_task_result(event_type, task_result),
                                      task_name,
                                      task_result))

    def summarize_task_result(self, event_type, result):
        if event_type == "on_ok":
            if result.get('changed', False):
                return "fail"
            else:
                return "pass"

        elif event_type == "on_skipped":
            return "skipped"

        # return 'error' for everything else
        elif event_type == "on_failed":
            return "error"

        elif event_type == "on_unreachable":
            return "error"

        else:
            return "error"



    # Ansible Callback API
    #
    #
    #
    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.splitext(os.path.basename(playbook._file_name))[0]

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.append_result(result, "on_failed")

    def v2_runner_on_ok(self, result):
        self.append_result(result, "on_ok")

    def v2_runner_on_skipped(self, result):
        self.append_result(result, "on_skipped")

    def v2_runner_on_unreachable(self, result):
        self.append_result(result, "on_unreachable")

    def v2_playbook_on_stats(self, stats):
        self.send_reports()
