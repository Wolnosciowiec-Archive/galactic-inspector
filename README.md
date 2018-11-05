ssh-server-audit
================

Tiny application for centralized monitoring of remote servers.
In comparison to traditional health checks `ssh-server-audit` is executing commands using _SSH_.

Functionality:
- SOCKS proxy support: Possibility to hide service in the internet using TOR
- Health checks: Execute remote command, check exit code. Execute other command on failure to repair simple things
- Authenticity check: Check if remote filesystem is untouched by third-party (eg. by hosting provider, by other hosting users, by the government)

### Quick start

1. Create a configuration file, example:

```
test_vagrant_volume:       # name it as you want
    socks_host: ""         # (optional) leave empty if not using socks
    socks_port: 9150       # (optional) but needs to be valid
    host: "localhost"
    port: 2422
    user: root
    password: "root"
    auth_method: password
    public_key: ""
    passphrase: ""
    checksum_method: "sha256sum"  # command name on remote server that will be doing checksums (eg. md5sum, sha256 sum)

    # files to verify on remote server, leave just "[]" without "" to not use checksums validation
    checksum_files:
        sh: '/bin/sh'
        bash: '/bin/bash'
        losetup: '$(whereis losetup|awk "{print \$2}")'

    # when at least one checksum would not match, then you can run a "repair command"
    # for example unmount an encrypted volume with logs, user identities, databases
    on_security_violation: "echo 'Something on security violation'"

    # health checks, use "[]" without "" to not use health checks.
    healthchecks:
        - command: "ps aux |grep nginx"
          on_failure: "echo 'Something on failure'"
        - command: "ps aux |grep bash"
          on_failure: "echo 'This should not show'"

```