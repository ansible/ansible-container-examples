# elk-stack

This is example was taken from the [Elasticsearch, Logstash, Kibana (ELK) Docker image documentation](https://elk-docker.readthedocs.io/).

The intention of this example is to present a how-to for using [Jinja](http://jinja.pocoo.org) templating within *container.yml*. Take a look at 
[Quck Tour](http://docs.ansible.com/ansible-container/tour.html), if you're unfamiliar with *contianer.yml* and its role in an Ansible Container project.

Here is the *container.yml* included in this project:

```
version: "1"
defaults:
  beats_access_port:     9200
  forwarder_access_port: 5000
  kibana_access_port:    5601
  logstash_access_port:  5044
  nginx_access_port:     8080
services:
  elk:
    image: sebp/elk
    ports:
      - "{{ kibana_access_port }}:5601"
      - "{{ beats_access_port }}:9200"
      - "{{ logstash_access_port }}:5044"
      - "{{ forwarder_access_port }}:5000"
    {% if logstash_data %}
    volumes:
      - {{ logstash_data }}:/var/lib/elasticsearch
    {% endif %}
  nginx:
    image: nginx
    links:
      - elk:elk
    ports:
      - "{{ nginx_access_port }}:8000"
    command: /usr/local/bin/start.sh
    user: nginx
    {% if nginx_log_data %}
    volumes:
      - {{ nginx_log_data }}:/var/log/nginx
    {% endif %}
registries: {}
```

When Ansible Container reads this *container.yml* it will pass it through Jinja template rendering and use the result. For template rendering to work Jinja needs to know the values of the variables 
referenced in each expression. If you are unfamiliar with Jinja and template expressions, please review [the Jinja docs](http://jinja.pocoo.org/docs/dev/). Variable definitions can be passed to 
Ansible Container using the following methods:

- Use the *--var-file* option, pass the path of a YAML or JSON file containing definitions
- Provide a *defaults* top-level section in the *container.yml* file
- Define  *AC_* environment variables that correspond to the Jinja variables  

Let's take a look at the *container.yml* starting with the *elk* services. It uses an ELK stack image, *sebp/elk*, pulled from Docker Hub as its base iamge, and it exposes the standard ELK ports. 
Notice In the host portion of each of the defined port mappings the host portion is replaced with a Jinja expression, giving us the following expressions: `{{ kibana_access_port }}`, 
`{{ beats_access_port }}`, `{{ logstash_access_port }}`, and `{{ forwarder_access_port }}`. These expressions represent variable substitution in Jinja. If *kibana_access_port*, for example, 
is defined as 3000, then 3000 will be substituted for `{{ kibana_access_port }}` during template rendering.

Also, notice the *volumes* directive for the *elk* service. It's wrapped in a Jinja `{% if %} ... {% endif %}` expression. As you might guess just from reading it, if the 
*logstash_data* variable is defined, then a volume gets defined, and it binds the value of *logstash_data* to */var/lib/elasticsearch. Conversly, if *logstash_data* is not defined, the volume 
directive is excluded altogether form the final *container.yml*.  

The same thing has been done in the *nginx* service where variable substitution is used in the port mapping, and there is a conditionally defined volume for */var/log/nginx*. 

Notice toward the top of the file there is a *defaults* section. It provides default vaules for all of the variables used in the port definition. This insures that the port mappings will always work.
If no other definitions are provided using either *AC_* environment variables a variable file passed in using the *--var-file* option, then the default variables will be used. 

Variable precedence is given in the following order:

- defaults
- variable file
- environment variables

The default definition gets the lowest precedence, and environment variables receive the highest. This means that if we define a default value for *nginx_access_port* of *8080*, as in the above 
example, and we also define *AC_NGINX_ACCESS_PORT=9000* in the environment, the environment variable wins, and the value *9000* is used.

Since the above file provides a *default* section with port definitions, and the volume definitions are conditional, we can run a standard *build* command with no options and no additional variable
definitions, and it works:

```
$ ansible-container build
```

At runtime we can substitute different values using environment variables or variable file. For demo purposes, there is a *devel.yml* file included in the *ansible* directory providing some possible override 
values. You can run with those settings using the following command:

```
$ ansible-container --var-file devel.yml run
```

Using Jinja templating in *container.yml* provides some nice flexibility by allowing us to separate the configuration directives from the data, making it possible to substitute different configuration data
depending on the environment. Incorporating templating also gives us access to control structures like the *{% if %}* and *{% for %}* expressions, as demonstrated above. And, it's even possible
to share variable definitions with your plabyoook during the *build* process. For example, we could pass the variable file into the playbook run by doing the following:

```
$ ansible-container --var-file devel.yml build -- -e"@/ansible-container/ansible/devel.yml"  
```

Try it out. And please, let us know what you think. We would love to hear how you put this feature to use in your environment. For more information on Jinja templating in *container.yml* see 
[the templating guide on our doc site](http://docs.ansible.com/ansible-container/container_yml/template.html).

For help getting started or questions, you can find us in the following places:

* [Join the  mailing list](https://groups.google.com/forum/#!forum/ansible-container)
* [Open an issue](https://github.com/ansible/ansible-container/issues)
* Join the #ansible-container channel on irc.freenode.net.

