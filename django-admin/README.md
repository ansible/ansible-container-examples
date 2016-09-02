# django-admin

This is the same example project found in the [ansible-container repo](https://github.com/ansible/ansible-container/tree/master/example) with a twist. The images have 
been modified as needed to enable deployment on OpenShift.

## Why?

The original project can be deployed to Kubernetes as is. OpenShift is built on Kubernetes, but it has its own security requirements. First, container processes cannot
run as the *root* user. Even the entrypoint script cannot run as a privileged user. Second, the container must be able to run as an arbitrary user. 

Per the OpenShift [image creation guidelines](https://docs.openshift.org/latest/creating_images/guidelines.html):

> By default, OpenShift Origin runs containers using an arbitrarily assigned user ID. This provides additional security against processes escaping the container due 
> to a container engine vulnerability and thereby achieves escalated permissions on the host node.
>
> For an image to support running as an arbitray user, directories and files that may be written to by processes in the image should be owned by the root group and be 
> read/writable by that group. Files to be executed should also have group execute permissions.

## Changes

To make the example work within these constraints the following changes were made:

- For the postgresql service, switch the base image to [openshift/postgresql-92-centos7](https://hub.docker.com/r/openshift/postgresql-92-centos7/)
- For the django service, change file permissions on any directories and files the django process will access.   
- For the static service, also change file permissions on any directories and files the nginx process will access.

Setting file permissions entails changing the group to *root* and granting read, write access to the group. This works because the arbitrary user employed by OpenShift is a member 
of *root*. The file permission changes are applied in the [ansible/main.yml](https://github.com/ansible/ansible-container-examples/blob/master/django-admin/ansible/main.yml) playbook. 
If you compare to the original [example/ansible/main.yml](https://github.com/ansible/ansible-container/blob/develop/example/ansible/main.yml) playbook, you'll see the specific changes.
  
## Requirements 

To complete the deployment to OpenShift you will need the following:

- An [OpenShift Online Next Geneneration](https://www.openshift.com/devpreview/) developer preview account.
- The OpenShift CLI installed. Log into your OpenShift Next Generation account and view [command line tools page](https://console.dev-preview-stg.openshift.com/console/command-line)
- Ansible Container installed. See the [Ansible Container install guide](http://docs.ansible.com/ansible-container/installation.html) for assistance.
- A local copy of the ansible-container-examples repo:

    ```
    git clone https://github.com/ansible/ansible-container-examples.git
    ```

### Build

Start by building the example. Run the *build* command from within the *django-admin* directory found in your local copy of the project: 

```
$ cd ansible-container-examples/django-admin
$ ansible-container build
```

The *build* command creates the images for the sample application. There are 4 services defined in [ansible/container.yml](https://github.com/ansible/ansible-container-examples/blob/master/django-admin/ansible/container.yml) 
To build the images a container is created and started for each service, along with an Ansible Build container for running Ansible. A total of 5 containers will be started.

The [ansible/main.yml playbook](https://github.com/ansible/ansible-container-examples/blob/master/django-admin/ansible/main.yml) is executed on the Ansible Build container with an inventory
consisting of the 4 service names defined in *container.yml*. If you examine *main.yml*, you will notice that each play has a *hosts* directive listing one or more of the service names where 
tasks will be executed. If you're an experienced Ansible user, this should look and feel very familiar. Ansible playbook execution is exactly the same here as it is in any other environment 
with one exception. Instead of using SSH to communicate to the remote nodes, we're using the Docker connection plugin.

As the build command proceeds, output from the playbook execution will appear, marking the completion of each task and play. Once completed, containers are committed and stopped. A Docker 
*commit* is essentially a snap-shot of the container at that moment, and it becomes an image. When the build process is fully complete, there will be 4 new images available in the local 
image cache.

Example output from running the *build* command follows:

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

Checking the local image cache shows the new images: 

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
an attached state, streaming stdout of each container terminal window. The containers will remain active until the terminal session is
killed or the kill signal is sent by pressing *Ctrl-c*.

With the containers running, you should be able to open a browser window and access the application on port 8100 of the Docker daemon host. The root of the application 
is */admin*. So to get to the application in your browser, you'll enter: `http://<Docker host IP>:8100/admin`

If you're running Docker Machine, the Docker daemon host is the IP of the Vagrant box. You can get the IP with the command `docker-machine ip <host name>`, where 
host name is the actual name of the host registered with VirtualBox Manager.

When everything is working, you will see th following in your browser:

![django-admin-img](https://github.com/ansible/ansible-container-examples/blob/master/images/django-admin.png)

## Login 

If you have not already done so, log into your OpenShift web console and create a project called *django-admin*. The application will be deployed into this project. 

You'll also need to authenticate with the OpenShift CLI. The instructions with the correct URL and access token can be found in your web console. Look for the support 
menu in the top right corner of the screen. Open it, and choose Command Line Tools. You will see a sample `oc login` command. Click the *click to show token* link and
copy the full command. 

Here's an example of logging in and setting the default project:

```
$ oc login https://api.dev-preview-stg.openshift.com --token=<your authentication token>
$ oc project django-admin

Now using project "django-admin" on server "https://api.dev-preview-stg.openshift.com:443"
```

## Push

Before the application can be deployed, the OpenShift cluster needs access to the image files. The easiest way to make the images accessible is to push them to the 
internal OpenShift registry, which you can do using Ansible Container. Note in the example below, we pass a --push-to value equal to the OpenShift registry followed 
by '/' and the name of the project: 

```
$ ansible-container push --push-to https://registry.dev-preview-stg.openshift.com/django-admin --username <username> --password <access token>
```

After successfully pushing the images, take a look at the images on OpenShift. Images on Openshift are referred to as *image streams*. Within your OpenShift web console
go to  [image streams](https://console.dev-preview-stg.openshift.com/console/project/django-admin/browse/images?main-tab=openshiftConsole%2Fbrowse&sub-tab=openshiftConsole%2Fbrowse-images). 
You should see a similar list of image streams:

![image streams](https://github.com/ansible/ansible-container-examples/blob/master/images/image_streams.png) 

## ShipIt

Next, run *shipit* to generate a deployment playbook and role. Specify the *openshift* engine, and use the --pull-from option to specify the URL the cluster will use to pull 
the images.

**NOTE** the URL for the *--pull-from* option is not the same URL used to push the images. The --pull-from URL will point to the internal registry using an IP address. 
View the [image streams page](https://console.dev-preview-stg.openshift.com/console/project/django-admin/browse/images?main-tab=openshiftConsole%2Fbrowse&sub-tab=openshiftConsole%2Fbrowse-images) in your OpenShift web console to get the correct IP address.

Follow the IP address with '/' + the name of the project. Your *shipit* command will be similar to the following:

```
$ ansible-container shipit openshift --pull-from 172.30.46.234:5000/django-admin

Images will be pulled from 172.30.46.234:5000/django-admin
Attaching to ansible_ansible-container_1
Cleaning up Ansible Container builder...
Role django-admin created.
```

Running *shipit* results in a playbook and a role being created in the *ansible* directory. You will see a *roles* directory and shipit-openshift.yml playbook:

```
$ ls -l ansible

total 88
-rw-r--r--  1 chouseknecht  staff  14760 Jul  8 12:25 ansible-container.log
-rw-r--r--  1 chouseknecht  staff   1403 Jul  8 12:17 container.yml
drwxr-xr-x  3 chouseknecht  staff    102 Jul  7 18:21 files
-rw-r--r--  1 chouseknecht  staff     10 Jun 26 13:14 inventory
-rw-r--r--  1 chouseknecht  staff      7 Jul  8 11:54 main.retry
-rw-r--r--  1 chouseknecht  staff   4005 Jul  8 11:57 main.yml
-rw-r--r--  1 chouseknecht  staff    148 Jun 26 13:14 requirements.txt
drwxr-xr-x  3 chouseknecht  staff    102 Jul  6 02:09 roles                    <----
-rw-r--r--  1 chouseknecht  staff    179 Jul  6 02:09 shipit-openshift.yml     <----
```

## Deploy

From within the *ansible* directory run he playbook to deploy the app.

```
$ cd ansible
$ ansible-playbook shipit-openshift.yml
```

After the playbook completes, take a look at the services, pods and routes created by the role:

```
$ oc get service

NAME         CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
django       172.30.9.83     <none>        8080/TCP   2d
postgresql   172.30.53.172   <none>        5432/TCP   2d
static       172.30.6.139    <none>        80/TCP     2d


$ oc get pod

NAME                 READY     STATUS    RESTARTS   AGE
django-1-aw6s3       1/1       Running   0          2h
postgresql-1-19z6q   1/1       Running   0          2h
static-1-rwn1d       1/1       Running   0          2h

$ oc get route

NAME        HOST/PORT                                                       PATH      SERVICE          TERMINATION   LABELS
static-80   static-80-django-admin.b795.dev-preview-stg.openshiftapps.com             static:port-80                 app=django-admin,service=static

```

The pods are created using deployments:

```
$ oc get dc

NAME         REVISION   REPLICAS   TRIGGERED BY
django       1          1          config
postgresql   1          1          config
static       1          1          config

```

The route contains the URL for accessing the application via web browser. It's the full *openshfitapps.com* domain listed under *HOST/PORT* in the output from `oc get route`. 
Add '/admin' to view the same log-in page viewed when the app ran locally.

**NOTE** The domain name is randomly generated by OpenShift. Use the domain generated by OpenShift in your environment, not the one listed in the above `oc get route`
output example.

Using the above output from `oc get route`, the log-in page to our app is accessed with the following: 

```
http://static-80-django-admin.b795.dev-preview-stg.openshiftapps.com/admin
```

With not too much effort we were able to launch the app on OpenShift and demonstrate how Ansible Container manages the container lifecycle. If you're interested in 
learning more, or have questions, please let us know how we can help. The best ways to reach us are:

* [Join the  mailing list](https://groups.google.com/forum/#!forum/ansible-container)
* [Open an issue](https://github.com/ansible/ansible-container/issues)
* Join the #ansible-container channel on irc.freenode.net.
