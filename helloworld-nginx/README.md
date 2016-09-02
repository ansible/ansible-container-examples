# Ansible-continer HelloWorld

Here is a quick `ansible-container` HelloWorsld deployment running Nginx. 

The config creates a single Centos 7 container running nginx exposed on port 8080. 

This GIST assumes you have read the `ansible-container` docs and have a sucessful install of the app and its prerequisits.

## Install
1. Run `ansible-container init`
2. In the `ansible` directory created populate `container.yml` and `main.yml` with the content below
3. In the `ansible` directory creat a directory called `files`
4. In the `files` dorectory create a file called `index.html` and copy the content below or your own custom HTML
5. Run `ansible-container build`
6. Run `ansible-container run`

You should now be able to browse to `http://localhost:8080` in your local browser and see the content of `files/index.html`.
