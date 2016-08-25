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

After the repo, you can create a live container and SSH into it.

```
$ cd projects
$ git clone https://github.com/ansible/ansible-container-examples.git
``` 

Start by building the container image. Change into the sshd example directory and execute the build command. This will create image *sshd-ssh*: 

```
$ cd ansible-container-examples/sshd
$ ansible-container build
```

Next, run a container using the new image. The following will start the container in detached mode:

```
$ ansible-container run -d
```

Check to see which host port was mappped to port 22 on the container:

```
$ docker ps

CONTAINER ID        IMAGE               COMMAND               CREATED             STATUS              PORTS                   NAMES
d3a8cd2cd5e6        sshd-ssh:latest     "/usr/sbin/sshd -D"   6 seconds ago       Up 5 seconds        0.0.0.0:32786->22/tcp   ansible_ssh_1
```

In the above example host port 32786 was mapped to port 22 on the container. Note that this is configured in container.yml. If you want to map
container port 22 to a specific host port, modify the *ports* option. 

We're ready to SSH into the container. If you're using Docker Machine, you will first need the IP address of the host VM. The following command 
will provide the IP. Repalce *default* with the name of your VM:

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

