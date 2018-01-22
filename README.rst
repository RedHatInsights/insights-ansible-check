Custom Insights Policies as Ansible Playbooks, Ansible Playbooks that act as Insights Policies
---------------

The general idea is that we run mostly normal Ansible playbooks in ``--check`` mode, and
interpret the result of each task in the playbook as a conformance test, and then forward
those interpreted conformace test results to Insights for display.

Insights Check Mode
---------

In Insights Check Mode, each playbook task is treated as a conformance test.  If the task
completes with a status "ok", the conformance test passes.  If the task completes with a status
"changed", the conformance test fails.  If the task is skipped, the task is ignored for the
purposes of conformance testing.  Any other task status is treated as an error in the
conformance testing.

When a playbook is run in Insights Check Mode, the result will be forwarded to the Insights
server.  A new "CHECKMODE SUMMARY" is added to the end of the normal output from running
the playbook to show the data forwarded to Insights.

In the example below are two RHEL 6.6 machines, one with FIPS mode enabled one without::

    $ ./insights-policy-check --limit=gavin-rhel66-nofips,gavin-rhel66-yesfips playbooks/fips-mode-check.yml

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
        fail : fips mode must be enabled
    gavin-rhel66-yesfips		31efea29-6020-4dfa-be47-f1aca02fba28
        pass : fips mode must be enabled

In the CHECKMODE SUMMARY, the final "pass" and "fail" are the important bits.  The label
"fail" is a big red "X", no this system is NOT in fips mode.  The label "pass" is a green
checkmark, yes the system is in fips mode.

When a playbook is run in --check mode, the status "changed" doen't mean actually changed, it
means would have been changed, not in the state specified by the task.  This is why we map
"changed" to "fail".

The status "ok" means the system is in the state specified by the task, so we map that to "pass".

Note that the status "ok" is also returned for tasks that don't specify a state for the system,
but instead just gather facts, or other information from the system.  The initial, implicit,
"Gathering Facts" task is an example of this.  It would be better if Insights Check Mode didn't
treat these two different meanings of "ok" the same; if the task is just a fact gathering task,
it should not be treated as a conformance test, but in general these two cases can not be
distinguished.  In the specific case of the "Gathering Facts" task, we can distinguish that
instance, and not include it in the CHECKMODE SUMMARY.



The Insights Check Mode command:
----------

The command ``insights-policy-check`` runs an Ansible playbook in Insights Check Mode.  This
command is just a wrapper around the ``ansible-playbook`` command.  This wrapper script enables
the Ansible plugins that implement Insights Check Mode.

The command ``insights-policy-check`` takes exactly the same arguments as ``ansible-playbook``


Preparing to run insights-policy-check
--------------------------------------

Before you can run ``insights-policy-check`` you must install its dependacies, and configure your
systems to talk to the Insights service.

Like Ansible, ``insights-policy-check`` has a Control Machine and one or more Managed Nodes which
have different installation and configuration requirements.  The Control Machine is where
``insights-policy-check`` is actually run.  The Managed Nodes are the systems where conformance
will be tested.


Preparing the Control Machine
-----------------------------

Ansible must be installed on the system where you run the insights-policy-check command, and
you must have set up an Ansible Inventory for any systems you want to run ``insights-policy-check``
against.  See `Ansible Installation
<http://docs.ansible.com/ansible/latest/intro_installation.html>`_ for instructions on how to install
and configure Ansible.

If your Control Machine is a RHEL6 or RHEL7 system, the shell scripts ``support-scripts/rhel6-install-ansible.sh`` and ``support-scripts/rhel7-install-ansible.sh`` will install Ansible on those operating systems.  Additionally you will need to configure an Ansible inventory on your Control machine for your Managed Nodes.  See `Ansible Inventory <http://docs.ansible.com/ansible/latest/intro_inventory.html>`_.

Additionally the Python module ``requests`` must also be installed on the Control Machine::

  yum install -y python-requests

Finally, ``insights-policy-check`` must be able to log into the Insights Service.  If you are
going to run ``insights-policy-check`` as root, and your Control machine is registered to either
Red Hat Insights or Red Hat Subscription Manager, ``insights-policy-check`` can log into
Insights already.

Otherwise, you must put a Red Hat username/password in ``~/.insights.conf``::
  [insights-client]
  username=<USERNAME>
  password=<PASSWORD>

Where ``<USERNAME>`` and ``<PASSWORD>`` are valid for Red Hat Insights (Red Hat Portal,
RHN, or RHSM).


Preparing the Managed Nodes
---------------------------

Each Managed node must have Insights installed, and it must be registered to the Insights service.

Additionally, each Managed node must have some additional configuration to allow ``insights-policy-check`` to be able to get the Insights System ID off each Managed node.

The Ansible playbook ``support-playbooks/redhat-insights-registered.yml`` ensures all these
requirements.  On the Control Machine, run::

     ansible-playbook -l <HOSTLIST> support-playbooks/redhat-insights-registered.yml

Where <HOSTLIST> is a comma separated list of all of the Managed nodes.




Running and Installing ``insights-policy-check``
---------------------------------

Once the prerequisites (Ansible and python-requests) on the Control machine are installed
``insights-policy-check`` can be run.

For testing and demoing purposes, the ``insights-policy-check`` script can be run directly
from the git repo::

   ./insights-policy-check --limit=localhost playbooks/no-dummy-hostname.yml

It can also be installed onto the Control machine.  This will put the Insights Check Mode plugins
into the standard Ansible plugins directories (/usr/share/ansible), and put the script into /usr/bin::

  sudo make install



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

    ./insights-policy-check --limit=<HOST PATTERN> <CHECK PLAYBOOK>

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
``insights-policy-check`` must log into Insights from the control system.  Second, it
must be able to get the Insights System ID off each target system.

For ``insights-policy-check`` to be able to log into Insights from the control system.

For the Control system, if you are running  ``insights-policy-check`` as root, and your
control system is registered to either Red Hat Insights or Red Hat Subscription Manager,
``insights-policy-check`` can log into Insights already.

Otherwise, you must put a Red Hat username/password in ``~/.insights.conf``::
  [insights-client]
  username=<USERNAME>
  password=<PASSWORD>

Where ``<USERNAME>`` and ``<PASSWORD>`` are valid for Red Hat Insights (Red Hat Portal,
RHN, or RHSM).

For the Managed nodes, for ``insights-policy-check`` to be able to get the Insights System ID
off each target system, the Insights collector (redhat-access-insights) must be installed
and registered on each target system, and the Insights fact plugin must be installed on
each target system.  Ferthermore, if the your playbooks are not running as root (become: True),
then you must adjust the permisssions on the file containing the Insights System ID so that
non-root users can read it.  The playbook ``redhat-insights-registered.yml`` in
``support-playbooks`` will ensure all of these are true::

     ansible-playbook -l <HOSTLIST> support-playbooks/redhat-insights-registered.yml

Where <HOSTLIST> is all of the target systems.



Demoing and Testing 'insights-policy-check' with ``pip``
------

``insights-policy-check`` can be installed using pip on those systems that have and use pip.
