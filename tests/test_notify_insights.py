

from fake_package.notify_insights import CallbackModule

ALL_RESULTS=[]
ALL_FINAL_OUTPUTS = {}

def add_task_result(host_name, task_result_summary, task_name, task_result):
    ALL_RESULTS.append({
        "host_name": host_name,
        "event_type": "on_ok",
        "task_name": task_name,
        "task_result": task_result,
        })
    if host_name not in ALL_FINAL_OUTPUTS:
        ALL_FINAL_OUTPUTS[host_name] = {
            "raw_output": "",
            "check_results": [],
        }
    ALL_FINAL_OUTPUTS[host_name]["check_results"].append({
        "name": task_name,
        "result": task_result_summary,
        })

add_task_result(host_name="gavin-rhel66-nofips",
     task_result_summary="fail",
     task_name="fips mode must be enabled",
     task_result={
         "failed": False,
         "changed": True,
         "evaluated_to": False,
         "assertion": "ansible_fips",
     })
add_task_result(host_name="gavin-rhel66-yesfips",
     task_result_summary="pass",
     task_name="fips mode must be enabled",
     task_result={
         "failed": False,
         "changed": False,
     })
add_task_result(host_name="gavin-rhel66-nofips",
     task_result_summary="pass",
     task_name="hostname must not be \"localhost\"",
     task_result={
         "changed": False,
     })
add_task_result(host_name="gavin-rhel66-yesfips",
     task_result_summary="pass",
     task_name="hostname must not be \"localhost\"",
     task_result={
         "changed": False,
     })
add_task_result(host_name="gavin-rhel66-nofips",
     task_result_summary="fail",
     task_name="prelink package must be absent (not installed)",
     task_result={
         "invocation": {
             "module_args": {
                 "allow_downgrade": False,
                 "name": [
                     "prelink"
                 ],
                 "list": None,
                 "disable_gpg_check": False,
                 "conf_file": None,
                 "install_repoquery": True,
                 "state": "absent",
                 "disablerepo": None,
                 "update_cache": False,
                 "enablerepo": None,
                 "exclude": None,
                 "security": False,
                 "validate_certs": True,
                 "installroot": "/",
                 "skip_broken": False
             }
         },
         "changed": True,
         "changes": {
             "removed": [
                 "prelink"
             ]
         },
         "results": []
     })
add_task_result(host_name="gavin-rhel66-yesfips",
     task_result_summary="pass",
     task_name="prelink package must be absent (not installed)",
     task_result={
         "msg": "",
         "rc": 0,
         "invocation": {
             "module_args": {
                 "allow_downgrade": False,
                 "name": [
                     "prelink"
                 ],
                 "list": None,
                 "disable_gpg_check": False,
                 "conf_file": None,
                 "install_repoquery": True,
                 "state": "absent",
                 "disablerepo": None,
                 "update_cache": False,
                 "enablerepo": None,
                 "exclude": None,
                 "security": False,
                 "validate_certs": True,
                 "installroot": "/",
                 "skip_broken": False
             }
         },
         "changed": False,
         "results": [
             "prelink is not installed"
         ]
     })
add_task_result(host_name="gavin-rhel66-nofips",
     task_result_summary="fail",
     task_name="kernel package must be the latest",
     task_result={
         "changed": True,
         "results": [],
         "msg": "",
         "rc": 0,
         "invocation": {
             "module_args": {
                 "allow_downgrade": False,
                 "name": [
                     "kernel"
                 ],
                 "list": None,
                 "disable_gpg_check": False,
                 "conf_file": None,
                 "install_repoquery": True,
                 "state": "latest",
                 "disablerepo": None,
                 "update_cache": False,
                 "enablerepo": None,
                 "exclude": None,
                 "security": False,
                 "validate_certs": True,
                 "installroot": "/",
                 "skip_broken": False
             }
         },
         "changes": {
             "updated": [
                 [
                     "kernel",
                     "2.6.32-696.16.1.el6.x86_64 from rhel-6-server-rpms"
                 ]
             ],
             "installed": []
         }
     })
add_task_result(host_name="gavin-rhel66-yesfips",
     task_result_summary="fail",
     task_name="kernel package must be the latest",
     task_result={
         "changed": True,
         "results": [],
         "msg": "",
         "rc": 0,
         "invocation": {
             "module_args": {
                 "allow_downgrade": False,
                 "name": [
                     "kernel"
                 ],
                 "list": None,
                 "disable_gpg_check": False,
                 "conf_file": None,
                 "install_repoquery": True,
                 "state": "latest",
                 "disablerepo": None,
                 "update_cache": False,
                 "enablerepo": None,
                 "exclude": None,
                 "security": False,
                 "validate_certs": True,
                 "installroot": "/",
                 "skip_broken": False
             }
         },
         "changes": {
             "updated": [
                 [
                     "kernel",
                     "2.6.32-696.16.1.el6.x86_64 from rhel-6-server-rpms"
                 ]
             ],
             "installed": []
        }
     })
add_task_result(host_name="gavin-rhel66-nofips",
     task_result_summary="pass",
     task_name="sshd config file must be owned by root and only readable by root",
     task_result={
         "group": "root",
         "uid": 0,
         "changed": False,
         "owner": "root",
         "state": "file",
         "gid": 0,
         "secontext": "system_u:object_r:etc_t:s0",
         "mode": "0600",
         "path": "/etc/ssh/sshd_config",
         "invocation": {
             "module_args": {
                 "directory_mode": None,
                 "force": False,
                 "remote_src": None,
                 "path": "/etc/ssh/sshd_config",
                 "owner": "root",
                 "follow": False,
                 "group": "root",
                 "unsafe_writes": None,
                 "state": None,
                 "content": None,
                 "serole": None,
                 "diff_peek": None,
                 "setype": None,
                 "selevel": None,
                 "original_basename": None,
                 "regexp": None,
                 "validate": None,
                 "src": None,
                 "seuser": None,
                 "recurse": False,
                 "delimiter": None,
                 "mode": 384,
                 "attributes": None,
                 "backup": None
             }
         },
         "diff": {
             "after": {
                 "path": "/etc/ssh/sshd_config"
             },
             "before": {
                 "path": "/etc/ssh/sshd_config"
             }
         },
         "size": 3879
     })
add_task_result(host_name="gavin-rhel66-yesfips",
     task_result_summary="pass",
     task_name="sshd config file must be owned by root and only readable by root",
     task_result={
         "group": "root",
         "uid": 0,
         "changed": False,
         "owner": "root",
         "state": "file",
         "gid": 0,
         "secontext": "system_u:object_r:etc_t:s0",
         "mode": "0600",
         "path": "/etc/ssh/sshd_config",
         "invocation": {
             "module_args": {
                 "directory_mode": None,
                 "force": False,
                 "remote_src": None,
                 "path": "/etc/ssh/sshd_config",
                 "owner": "root",
                 "follow": False,
                 "group": "root",
                 "unsafe_writes": None,
                 "state": None,
                 "content": None,
                 "serole": None,
                 "diff_peek": None,
                 "setype": None,
                 "selevel": None,
                 "original_basename": None,
                 "regexp": None,
                 "validate": None,
                 "src": None,
                 "seuser": None,
                 "recurse": False,
                 "delimiter": None,
                 "mode": 384,
                 "attributes": None,
                 "backup": None
             }
         },
         "diff": {
             "after": {
                 "path": "/etc/ssh/sshd_config"
             },
             "before": {
                 "path": "/etc/ssh/sshd_config"
             }
         },
         "size": 3879
     })


def test_notify_insights():
    m = CallbackModule()
    for each in ALL_RESULTS:
        m._append_result(**each)


    for host in m.items.keys():
        assert ALL_FINAL_OUTPUTS[host] == m._build_log(m.items[host])
