
from ..service.ssh import SSH


class Healthcheck:
    _command = ''
    _on_failure = ''

    def __init__(self, command: str, on_failure: str, exec_repair_on_sec_violation: bool):
        self._command = command
        self._on_failure = on_failure
        self._exec_repair_on_sec_violation = exec_repair_on_sec_violation

    def get_command(self):
        return self._command

    def get_on_failure(self, security_violation_active: bool):
        if security_violation_active and not self._exec_repair_on_sec_violation:
            return ''

        return self._on_failure


class Node:
    DEFINITION = {
        'host': str,
        'port': int,
        'user': str,
        'verify_ssh_fingerprint': bool,
        'password': str,
        'auth_method': str,
        'public_key': str,
        'passphrase': str,

        'ssh_auth_timeout': int,
        'ssh_banner_timeout': int,
        'ssh_tcp_timeout': int,

        # command name or path, example: md5sum, sha256sum
        'checksum_method': str,
        'checksum_files': dict,

        # use socks proxy to connect to SSH with
        # (allows to hide this service behind TOR network)
        'socks_host': str,
        'socks_port': int,

        'healthchecks': list,

        # a command to execute in case of the checksum of any file would not match
        'on_security_violation': str
    }

    _config = {}
    _expectations = {}
    _healthchecks = []
    _ssh = None         # type: SSH

    # state
    _active_security_violation = False

    def __init__(self, config: dict, expectations: dict, ssh: SSH):
        self._config = config
        self._expectations = expectations
        self._ssh = ssh

        for check in config['healthchecks']:
            self._healthchecks.append(
                Healthcheck(check['command'], check['on_failure'], check['on_failure_even_if_security_violation'])
            )

    def get_address(self) -> str:
        return self._config['host']

    def get_port(self) -> int:
        return self._config['port']

    def get_user(self) -> str:
        return self._config['user']

    def get_password(self) -> str:
        return self._config['password']

    def get_auth_method(self) -> str:
        return self._config['auth_method']

    def get_public_key(self) -> str:
        return self._config['public_key']

    def get_passphrase(self) -> str:
        return self._config['passphrase']

    def get_expected_checksum(self, name: str) -> str:
        return self._expectations[name] if name in self._expectations else ''

    def get_checksum_method(self):
        return self._config['checksum_method']

    def get_socks_port(self) -> int:
        return self._config['socks_port']

    def get_socks_host(self) -> str:
        return self._config['socks_host']

    def get_what_to_do_on_security_violation(self):
        return self._config['on_security_violation']

    def get_health_checks(self) -> list:
        return self._healthchecks

    def get_checksum_files(self) -> dict:
        return self._config['checksum_files']

    def get_ssh(self):
        return self._ssh

    def is_verify_ssh_fingerprint(self):
        return self._config['verify_ssh_fingerprint']

    def has_active_security_violation(self) -> bool:
        return self._active_security_violation

    def set_active_security_violation_marking(self, is_active: bool):
        self._active_security_violation = is_active

    def __repr__(self):
        return 'Node <' + self.get_user() + '@' + self.get_address() + ':' + str(self.get_port()) + '>'
