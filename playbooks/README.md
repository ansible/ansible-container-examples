Playbooks
=========

For each role in the roles directory, provide a sample playbook to execute the role. Given a local copy of this repo, examples will execute with the following
commands: 

```
    $ cd ansible-container-examples/playbooks
    $ ansible-playbook <playbook-name>
```

For convenience inventory and ansible.cfg files are provided in this directory. The inventory contains 'localhost' only, and the ansible.cfg file sets *roles_path* and *inventory*. Playbooks added to this directory are expected to run on localhost.

Playbook execution requirements:

- [ansible](http://docs.ansible.com/ansible/intro_installation.html)
- [ansible-container](http://docs.ansible.com/ansible-container/installation.html)

Access to a Docker deamon is required. See the [ansible-container installation guide](http://docs.ansible.com/ansible-container/installation.html) for help setting up Docker and defining environment variables.
