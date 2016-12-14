# Ansible-container HelloWorld

Here is a quick [Ansible Container](https://github.com/ansible/ansible-container) HelloWorld deployment running Nginx. 

The config creates a single Centos 7 container running nginx exposed on port 8080. 

This GIST assumes you have read the [Ansible Container docs](https://docs.ansible.com/ansible-container), and have a sucessful install of Ansible Container.

## Install
1. Run `ansible-container init`
2. In the `ansible` directory populate `container.yml` and `main.yml` with the content below
3. In the `ansible` directory create a directory called `files`
4. In the `files` directory create a file called `index.html` and copy the content below, or use your own custom HTML
5. Run `ansible-container build`
6. Run `ansible-container run`

Open `http://localhost:8080` in your browser, and see the content of `files/index.html`. 

If you're running Docker Machine, in your terminal session run `open http://$(docker-machine ip default):8080`, replacing `default` with your machine name.
