# django-admin

This is the same example project found in the [ansible-container repo](https://github.com/ansible/ansible-container/tree/master/example) with a slight twist. 
Instead of using the [Postgresql](https://hub.docker.com/_/postgres/) image from Docker Hub, it uses an OpenShift v3 [compatible Postgresql image](https://hub.docker.com/r/openshift/postgresql-92-centos7/). 

## Why?

The standard Postgresql image found on Docker Hub does not comply with the [OpenShift-Specific Guidelines]
(https://docs.openshift.com/online/creating_images/guidelines.html) for creating images. In particular OpenShift v3 requires that an image run as an arbitrary User ID and 
not as a privileged user. The standard Postgresql image expects to run as a privileged user so that it can `chown` and `chmod` mount points, making them owned by and 
accessible to the postgresql user.

By swapping the standard Postgresql image out for an image supported by OpenShift v3 we can enable the use of the `shipit` command in ansible-container and deploy
this example to OpenShift v3. 

## Running the Example

There are two ways to use this example. It can be run locally or it can be deployed to a cluster. The catalyst for creating this example was demonstrating a deployment 
to OpenShift v3, so to that end this document will provide a walk through of running the app locally and deploying it to OpenShift. 

To get started you will need Ansible Container installed. Follow the [Ansible Container install guide](http://docs.ansible.com/ansible-container/installation.html) 
to make sure you install any prerequisites, including configuring access to a Docker daemon.

Next, clone a copy of the ansible-container-examples repo:

```
git clone https://github.com/ansible/ansible-container-examples.git
```

### Build

Start by building the example. Run the build command from within the *django-admin* directory found in the local copy of the project: 

```
$ cd ansible-container-examples/django-admin
$ ansible-container build
```

The build command creates the images for the sample application. There are 4 services defined in the [ansible/container.yml](https://github.com/ansible/ansible-container-examples/blob/master/django-admin/ansible/container.yml) 
file. A container is created for each, along with a build container for running Ansible. The [ansible/main.yml playbook](https://github.com/ansible/ansible-container-examples/blob/master/django-admin/ansible/main.yml) 
is executed on the build container.  Each of the 4 containers are nodes in the build container's inventory. The playbook is executed against the inventory of 4 
containers. Once playbook execution completes, the containers are stopped and a snapshot is taken of each container. The snapshot is the image. So once the process 
completes, we will see 4 new images available in the local image cache.

Running the build command produces the following output:

```
(Re)building the Ansible Container image.
Building Docker Engine context...
Starting Docker build of Ansible Container image (please be patient)...

... (A whole bunch of build and playbook execution output) ...

ansible-container_1  | PLAY RECAP *********************************************************************
ansible-container_1  | django                     : ok=15   changed=11   unreachable=0    failed=0
ansible-container_1  | gulp                       : ok=13   changed=9    unreachable=0    failed=0
ansible-container_1  | static                     : ok=10   changed=8    unreachable=0    failed=0
ansible-container_1  |
ansible_ansible-container_1 exited with code 0
Aborting on container exit...
Stopping ansible_static_1 ... done
Stopping ansible_gulp_1 ... done
Stopping ansible_django_1 ... done
Stopping ansible_postgresql_1 ... done
Exporting built containers as images...
Committing image...
Exported django-admin-gulp with image ID sha256:3c1f9b5518a1a6f4aeccb1a576562d61ac8cef836c70f7f9078147ca8303de22
Cleaning up gulp build container...
Committing image...
Exported django-admin-static with image ID sha256:15b944afc72e42c5f75a85dbb832c7966ba4ae1c071e36293a9b109f41ef55a6
Cleaning up static build container...
Committing image...
Exported django-admin-django with image ID sha256:d362d1b749c9235aab144d764168036702dff03455b06887aa6a401b1288c905
Cleaning up django build container...
Cleaning up Ansible Container builder...
```

Once the build completes, check the local image cache. You will see images for each of the django-admin services:

```
$ docker images

REPOSITORY                        TAG                 IMAGE ID            CREATED             SIZE
django-admin-django               20160705211710      d362d1b749c9        10 minutes ago      886 MB
django-admin-django               latest              d362d1b749c9        10 minutes ago      886 MB
django-admin-static               20160705211710      15b944afc72e        10 minutes ago      890.6 MB
django-admin-static               latest              15b944afc72e        10 minutes ago      890.6 MB
django-admin-gulp                 20160705211710      3c1f9b5518a1        10 minutes ago      354.2 MB
django-admin-gulp                 latest              3c1f9b5518a1        10 minutes ago      354.2 MB
ansible-container-builder         latest              00617d3fed58        20 minutes ago      884 MB
```

## Run

After building the application, run it locally to make sure everything works. The `ansible-container run` command will start each of the containers in 
an attached state, allowing the stdout of each container to dispaly on your terminal session window. The containers will remain active until the terminal session is
killed or you press *Ctrl-C* on your keyboard.

With the containers running, you should be able to open a browser window and access the application on port 8100 of the Docker daemon host. The root of the application 
is */admin*. So to get to the application in your browser, you'll enter: `http://<Docker host IP>:8100/admin`

If you're running Docker Machine, the Docker daemon host is the IP of the Vagrant box. You can get the IP with the command `docker-machine ip <host name>`, where 
host name is the actual name of the host registered with VirtualBox Manager.

When everything is working, you will see th following in your browser:

![django-admin-img](https://raw.githubusercontent.com/chouseknecht/misc/master/django-admin.png)

## ShipIt

Describe the shipit experience here...

