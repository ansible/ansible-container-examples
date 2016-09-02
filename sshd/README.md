# sshd

Should you do this? Not really. Containers are meant to be immutable, so there should be no reason to SSH into a container. If you need to 
poke around in a container for debugging purposes, the *right* way is to `docker exec -i -t <container_name> /bin/bash`.

But nevertheless, this question comes up all the time, "How can I run sshd in my container?" In fact, a developer recently opened an
issue at [Ansible Container](https://github.com/ansible/ansible-container) because he was having trouble figuring out the playbook to make this work.
So, here's the answer.

Keep in mind that [Ansible Container](https://github.com/ansible/ansible-container) does NOT use SSH when performing `ansible-container build`. It
uses `docker exec`. Once playbook execution completes it performs a `docker commit` to create an image from the changed container.

Enjoy! And stop changing things inside immutable containers! 

## Running the example

First, clone the Ansible Container Examples repo:

```
$ cd projects
$ git clone https://github.com/ansible/ansible-container-examples.git
``` 

Next we'll run the *build* command to create a container image that's capable of running *sshd*. The *build* command reads the *container.yml* and 
determine which services to start and which base images to use. In this case there is only one service defined, which we named *ssh*, and the base image 
is *ubuntu:14.04*. The *build* process will create and start a container using the *ubuntu14:04* image, which it pulls from Docker Hub. The name of
this container will be *ansible_sshd_1*. It also starts an Ansible Build container where it will run the playbook, *main.yml*. Playbook tasks will be 
executed on *ansible_sshd_1*, and communication between the two containers takes place using Ansible's Docker connection plugin.  

Run the following commands to start the *build* process:

```
$ cd ansible-container-examples/sshd
$ ansible-container build
```

As the *build* process runs, output from the playbook's execution will display, marking the completion of each task and play. Once the playbook completes 
the process performs a commit, taking a snapshot of the container, and creating a new image. 

Next, we'll run a container using the new image. The following will create and start a container in detached mode with the sshd process running inside:

```
$ ansible-container run -d
```

The sshd process inside the container is listening on port 22. Use `docker ps` to discover which host port is mappped to the container's port 22:

```
$ docker ps

CONTAINER ID        IMAGE               COMMAND               CREATED             STATUS              PORTS                   NAMES
d3a8cd2cd5e6        sshd-ssh:latest     "/usr/sbin/sshd -D"   6 seconds ago       Up 5 seconds        0.0.0.0:32786->22/tcp   ansible_ssh_1
```

In the above example host port 32786 was mapped to container port 22. This is configurable in *container.yml*. If you want to map
container port 22 to a specific host port, modify the *ports* option. 

We're ready to SSH into the container. If you're using Docker Machine, you will first need the IP address of the host VM. The following command 
will provide the IP. Replace *default* with the name of your VM:

```
$ docker-machine ip default
```

Either with the IP of the Docker Machine or localhost, if you're not running Docker Machine, SSH to the container with the following: 

```
$ ssh root@192.168.99.100 -p 32786
The authenticity of host '[192.168.99.100]:32786 ([192.168.99.100]:32786)' can't be established.
ECDSA key fingerprint is SHA256:NgVOKNssA0OeTUFiFJA1OONpLQN7ezfv5FJmkKiR4eA.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '[192.168.99.100]:32786' (ECDSA) to the list of known hosts.
root@192.168.99.100's password:
```

The password is *password*. This gets set on line 4 in main.yml.

**NOTE** Obviously keeping clear text passwords in an unencrypted playbook is not safe. For ways to encrypt files and pass them into your playbook
or encrypt the entire playbook see the [ansible-vault docs](http://docs.ansible.com/ansible/playbooks_vault.html).

For more information on [Ansible Container](https://github.com/ansible/ansible-container), please visit our [docs site](https://docs.ansible.com/ansible-container). If you 
have question or need help getting started, please reach out to us using one of the following:

* [Join the  mailing list](https://groups.google.com/forum/#!forum/ansible-container)
* [Open an issue](https://github.com/ansible/ansible-container/issues)
* Join the #ansible-container channel on irc.freenode.net.


