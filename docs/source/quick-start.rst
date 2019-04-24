Quick start
===========

Application is written in Python 3, the required Python version is at least 3.6
If you would decide to use a docker image, then you do not need to worry about the technologies and dependencies.

**Most important notes:**

- "/root/.ssh" and "/root/.ssh-server-audit/expectations" needs to be a volume eg. named volume, as the expectations are generated once, also the SSH keys needs to be persisted
- You need to pass your configuration file to the container, and place it under "/usr/local/etc/ssh-server-audit"

Installing with PIP and running natively
----------------------------------------

.. code:: bash

    pip install galactic-inspector

Running with docker
-------------------

.. code:: bash

    docker run \
     -p 80:80 \
     -v "./containers/ssh-server-audit:/usr/local/etc/ssh-server-audit" \
     -v "expectations:/root/.ssh-server-audit/expectations" \
     -v "openssh:/root/.ssh" \
     --entrypoint="ssh-server-audit --port=80 --sleep-time=500 --expectations-directory=/root/.ssh-server-audit/expectations"
     wolnosciowiec/ssh-server-audit


Running with docker-compose
---------------------------

.. code:: yaml

    version: '2'
    volumes:
        expectations:
        openssh:
    services:
        app_auditor:
            image: wolnosciowiec/ssh-server-audit:latest
            volumes:
                # here you attach your configuration file as a volume
                - "./containers/ssh-server-audit:/usr/local/etc/ssh-server-audit"
                - "expectations:/root/.ssh-server-audit/expectations"
                - "openssh:/root/.ssh"
            expose:
                - 80
            ports:
                - "80:80"
            environment:
                # gateway configuration (see RiotKit's Harbor, nginx-letsencrypt-companion, nginx proxy-gen)
                - VIRTUAL_HOST=audit.localhost
                - VIRTUAL_PORT=80
            #depends_on:
            #    - tor
            entrypoint: "ssh-server-audit --port=80 --sleep-time=500 --expectations-directory=/root/.ssh-server-audit/expectations"
