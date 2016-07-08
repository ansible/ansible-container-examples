# django-admin

This is the same example project found in the [ansible-container repo](https://github.com/ansible/ansible-container/tree/master/example) with a slight twist. The images have 
been modified as needed to make them deployable to OpenShift.  

## Why?

The original example project can be deployed to Kubernetes as is. OpenShift is built on Kubernetes, but it has its own Security requiremens. First, container processes cannot
run as the *root* user. Even the entrypoint script cannot run as a privileged user. Second, the container must be able to run as an arbitrary user. Per the OpenShift 
[image creation guidelines](https://docs.openshift.org/latest/creating_images/guidelines.html):

> By default, OpenShift Origin runs containers using an arbitrarily assigned user ID. This provides additional security against processes escaping the container due 
> to a container engine vulnerability and thereby achieves escalated permissions on the host node.
>
> For an image to support running as an arbitray user, directories and files that may be written to by processes in the image should be owned by the root group and be 
> read/writable by that group. Files to be executed should also have group execute permissions.

## Changes

So to make the example work within these contstraints the following changes were made:

- For the postgresql container, switch the base image to [openshift/postgresql-92-centos7](https://hub.docker.com/r/openshift/postgresql-92-centos7/)
- For the django container, change file permissions on any directories and files the django process will access.   
- For the static container, also change file permissions on any diretories and files the nginx process will access.

Setting file permissions entails setting the group to the *root* group and allowing full access to the group. This works becase the arbitrary user OpenShift will use to 
run the container will be part of the *root* group. For the django and static containers the file permission changes are applied to the ansible/main.yml playbook.
  
## Requirements 

There are two ways to use this example. It can be run locally or it can be deployed to a cluster. The catalyst for creating this example was demonstrating a deployment 
to OpenShift v3, so to that end this document will provide a walk through of running the app locally and deploying it to OpenShift. 

To complete this walk through you will need the following:

- An [OpenShift Online Next Geneneration](https://www.openshift.com/devpreview/) developer preview account.
- The OpenShift CLI installed.
- Ansible Container installed. Follow the [Ansible Container install guide](http://docs.ansible.com/ansible-container/installation.html) to make sure you install any prerequisites, including configuring access to a Docker daemon.
- A local copy of the ansible-container-examples repo:

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

Now checking the local image cache will produce the following: 

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
killed or you send the kill signal by pressing *Ctrl-c* at any point.

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

After successfully pushing the images, take a look at the images on OpenShift. Images on Openshift are ferred to as *image streams*. Go to *Browse -> Image Streams* in 
your OpenShift web console. You will something like the following:

![image streams](https://github.com/ansible/ansible-container-examples/blob/master/images/image_streams.png) 

## ShipIt

Next, run *shipit* to generate a deployment playbook and role. Specifiy the *openshift* engine, and use the --push-to option to specify the URL the cluster will use to locate 
and pull the images.

**NOTE** the URL for the *--pull-to* option is not the same URL used to push the images. The --pull-to URL will point to the internal registry using an IP address. 
View the *Browse -> Image Streams* page in your OpenShift web console. to get the correct IP address.

Follow the IP address with '/' + the name of the project. The *shipit* command will look similar to the following:

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
drwxr-xr-x  3 chouseknecht  staff    102 Jul  6 02:09 roles
-rw-r--r--  1 chouseknecht  staff    179 Jul  6 02:09 shipit-openshift.yml
```

## Deploy

Running the playbook will deploy the app. Run from within the *ansible* directory:

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

```

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

The route contains the URL for accessing the application via web browser. It's the full *openshfitapps.com* domain listed under *HOST/PORT*. Add '/admin' to view the 
same log-in page viewed while the app ran locally. Using the above output from the `oc get route` command as an example, we can access the app with the following: 

```
http://static-80-django-admin.b795.dev-preview-stg.openshiftapps.com/admin
```
