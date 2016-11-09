# Flask HelloWorld

Here is Flask HelloWorld example with [Ansible Container](https://github.com/ansible/ansible-container).

The config creates a CentOS 7 Container.

This GIST assumes you have read the [Ansible Container docs](https://docs.ansible.com/ansible-container), and have a sucessful install of Ansible Container.

## Install
1. Clone the Repo `git clone https://github.com/ansible/ansible-container-examples`.
2. Change Directory `cd ansible-container-examples/flask-helloworld/`.
3. Run `ansible-container build`.
4. Run `ansible-container run`.

You will find the content of `flask-helloworld/templates/index.html` on `http://localhost:5000`.
