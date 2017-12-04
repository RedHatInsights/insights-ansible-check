Custom Insights Rules as Ansible Playbooks, Ansible Playbooks that act as Insights Rules
---------------

This is just the beginnings of a proof of concept.

The general idea is that we run mostly normal Ansible playbooks in ``--check`` mode, and
interpret the result of each task in the playbook as a conformance test, and then forward
those interpreted results to Insights for display::

   ./insights-ansible-check --limit=localhost playbooks/no-dummy-hostname.yml

Ansible must be installed and an Ansible inventory file created for any of the examples
in this README to work.  See `Ansible Installation
<http://docs.ansible.com/ansible/latest/intro_installation.html>`_.

Insights Check Mode
---------

In Insights Check Mode, each playbook task is treated as a conformance test.  If the task
ends with a status "ok", the conformance test passes.  If the task ends with a status "changed",
the conformance test fails.  If the task is skipped, the task is ignored for the purposes of
conformance testing.  Any other task status is treated as an error in the conformance testing.

When a playbook is run in Insights Check Mode, the result will be forwarded to the Insights
server.  A new "CHECKMODE SUMMARY" is added to the end of the normal output from running
the playbook.

In the example below are two RHEL 6.6 machines, one with FIPS mode enabled one without::

    $ ./insights-ansible-check --limit=gavin-rhel66-nofips,gavin-rhel66-yesfips playbooks/fips-mode-check.yml 

    PLAY [all] *********************************************************************

    TASK [Gathering Facts] *********************************************************
    ok: [gavin-rhel66-nofips]
    ok: [gavin-rhel66-yesfips]

    TASK [fips mode must be enabled] ***********************************************
    changed: [gavin-rhel66-nofips]
    ok: [gavin-rhel66-yesfips]

    PLAY RECAP *********************************************************************
    gavin-rhel66-nofips        : ok=2    changed=1    unreachable=0    failed=0   
    gavin-rhel66-yesfips       : ok=2    changed=0    unreachable=0    failed=0   


    CHECKMODE SUMMARY **************************************************************
    gavin-rhel66-nofips		7ce9d65c-729d-4769-b038-db725bb69641
        failed : fips mode must be enabled
    gavin-rhel66-yesfips		31efea29-6020-4dfa-be47-f1aca02fba28
        passed : fips mode must be enabled

In the CHECKMODE SUMMARY, the final "passed" and "failed" are the important bits.  The label
"failed" is a big red "X", no this system is NOT in fips mode.  The label "passed" is a green
checkmark, yes the system is in fips mode.

When a playbook is run in --check mode, the status "changed" doen't mean actually changed, it
means would have been changed, not in the state specified by the task.  This is why we map
"changed" to "failed".

The status "ok" means the system is in the state specified by the task, so we map that to "passed".

Note that the status "ok" is also returned for tasks that don't specify a state for the system,
but instead just gather facts, or other information from the system.  The initial, implicit,
"Gathering Facts" task is an example of this.  It would be better if Insights Check Mode didn't
treat these two different meanings of "ok" the same; if the task is just a fact gathering task,
it should not be treated as a conformance test, but in general these two cases can not be
distinguished.  In the specific case of the "Gathering Facts" task, we can distinguish that
instance, and not include it in the CHECKMODE SUMMARY.


The Insights Check Mode command:
----------

The command ``insights-ansible-check`` runs an Ansible playbook in Insights Check Mode.  This
command is just a wrapper around the ``ansible-playbook`` command.

Ansible must be installed on the system where you run the insights-ansible-check command, and
you must have set up an Ansible Inventory for any systems you want to run ``insights-ansible-check``
against.

The command ``insights-ansible-check`` takes exactly the same arguments as ``ansible-playbook``

Playbooks for Insights Check Mode
------

There are currently several example playbooks:

playbooks/no-dummy-hostname.yml
  which fails if a system's hostname is 'localhost'.

playbooks/fips-mode-check.yml
  which checks that a system is in FIPS mode.
   
playbooks/prelink-absent-check.yml
  which checks that a system does not have the prelink package installed.

playbooks/examples.yml
  which shows more examples of how to write checks/tests

playbooks/error.yml
  A playbook with a task which will always fails to run correctly,
  showing how Insight Check Mode treats cases like this


Run these playbooks in Insights Check Mode::

    ./insights-ansible-check --limit=<HOST PATTERN> <CHECK PLAYBOOK>

where ``<HOST PATTERN>`` is a comma separated list of hosts to run the check against 
``<CHECK PLAYBOOK>`` is one of :

- playbooks/fips-mode-check.yml
- playbooks/prelink-absent-check.yml
- playbooks/no-dummy-hostname.yml

You can use your development machine as ``<HOST PATTERN>``, but for fips mode,
the results will probably be boring.

Any Ansible playbook can be run in Insights Check Mode, but because the playbooks are
always run in Ansible's ``--check`` mode, Ansible tasks using some Ansible Modules become
no-ops in Insights Check Mode.  Some Ansible modules are, by default, skipped when run
in ``--check`` mode, most notably the 'shell' and 'command' modules.  In Insights Check Mode,
any task that is skipped, is ignored.


Sending Data to Insights
------

To send Insights Check Mode data to the Insights service, two things must be true.  First,
``insights-ansible-check`` must log into Insights from the control system.  Second, it
must be able to get the Insights System ID off each target system.

For ``insights-ansible-check`` to be able to log into Insights from the control system, you
must put a Red Hat username/password in ``~/.insights.conf``::
  [insights-client]
  username=<USERNAME>
  password=<PASSWORD>

Where ``<USERNAME>`` and ``<PASSWORD>`` are valid for Red Hat Insights (Red Hat Portal,
RHN, or RHSM).

For ``insights-ansible-check`` to be able to get the Insights System ID off each target system,
the Insights collector (redhat-access-insights) must be installed and registered on each target
system, and the Insights fact plugin must be installed on each target system.  The
``insights-installer.yml`` playbook in ``support-playbooks`` will ensure both of these are true::

  ./ansible-playbook -l <HOSTLIST> support-playbooks/insights-installer.yml


Installing 'insights-ansible-check'
------

The command ``insights-ansible-check`` can be run directly from within the git repo, as all
the examples above do.

It can also be installed onto a system.

For RHEL6 and RHEL7 production systems, first ensure that Ansible is installed on the system.
See `Ansible Installation <http://docs.ansible.com/ansible/latest/intro_installation.html>`_.
Then::

    sudo make install


For enviroments with pip installed, or within Python virtual enviroments::

    sudo pip install .

will install both the command and the associate Ansible plugins onto the current system, along
with all of it's dependancies, including Ansible.
