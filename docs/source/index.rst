
Galactic Inspector
==================

Tiny application for centralized monitoring of remote servers.
In comparison to traditional health checks, the `galactic-inspector` is executing commands using **SSH**.

**Functionality:**

- SOCKS proxy support: Possibility to hide service in the internet using TOR
- Health checks: Execute remote command, check exit code. Execute other command on failure to repair simple things
- Authenticity check: Check if remote filesystem is untouched by third-party (eg. by hosting provider, by other hosting users, by the government)
- Detailed Slack/Mattermost notifications (also can be configured to work with SOCKS proxy) on each event

**Main conception**

The main conception is to monitor files integrity like some of IDS systems are doing.
What is different from other IDS systems is a native slack/mattermost support, focus on hiding the monitoring service
behind a proxy, and the size - it's tiny.

**High anonymity**

To protect the infrastructure against eg. government censorship in politically active projects, the IPS can be hidden behind
a SOCKS proxy eg. TOR network


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quick-start
   reference
   proxy

From authors
============

Project was started as a part of RiotKit initiative, for the needs of grassroot organizations such as:

- Fighting for better working conditions syndicalist (International Workers Association for example)
- Tenants rights organizations
- Various grassroot organizations that are helping people to organize themselves without authority

.. rst-class:: language-en align-center

*RiotKit Collective*
