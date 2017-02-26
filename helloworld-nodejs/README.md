# Ansible Container Demo

Demo of containerized Node.JS app deployment to OpenShift with Ansible Container

## Building and deploying the demo app

### Building the container
```
$ ansible-container build
```

### Pushing the container to a registry
```
$ ansible-container push --push-to docker.io/<username> --username <username>
```

### Generate playbook and role for the OpenShift deployment
```
$ ansible-container shipit openshift --pull-from docker.io/<username> --save-config
```

### Prepare the OpenShift environment
```
$ oc login --token=<token> --server=<openshift server>
$ oc new-project ansible-container-demo
```

### Deploy to OpenShift
```
$ cd ansible && ansible-playbook shipit-openshift.yml
```
