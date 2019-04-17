
from paramiko.ssh_exception import SSHException, BadHostKeyException
from ..service.ssh import SSH
from ..service.notify import Notifier


class Healthcheck:
    _command = ''
    _on_failure = ''

    def __init__(self, command: str, on_failure: str, exec_repair_on_sec_violation: bool):
        self._command = command
        self._on_failure = on_failure
        self._exec_repair_on_sec_violation = exec_repair_on_sec_violation

    def get_command(self):
        return self._command

    def __repr__(self):
        return self.get_command()

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

        'notifications': dict,

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
    _healthy = True
    _ssh = None         # type: SSH
    _notifier = None    # type: Notifier

    # state
    _active_security_violation = False

    def __init__(self, config: dict, expectations: dict, ssh: SSH):
        self._config = config
        self._expectations = expectations
        self._ssh = ssh

        for check in config['healthchecks']:
            self._healthchecks.append(
                Healthcheck(check['command'], check.get('on_failure', None),
                            check.get('on_failure_even_if_security_violation', False))
            )

    def get_address(self) -> str:
        return self._config['host']

    def get_port(self) -> int:
        return self._config.get('port', 22)

    def get_user(self) -> str:
        return self._config['user']

    def get_password(self) -> str:
        return self._config['password']

    def get_auth_method(self) -> str:
        return self._config.get('auth_method', 'password')

    def get_public_key(self) -> str:
        return self._config['public_key']

    def get_passphrase(self) -> str:
        return self._config['passphrase']

    def get_expected_checksum(self, name: str) -> str:
        return self._expectations[name] if name in self._expectations else ''

    def get_checksum_method(self):
        return self._config.get('checksum_method', 'sha256sum')

    def get_socks_port(self) -> int:
        return self._config.get('socks_port', 9050)

    def get_socks_host(self) -> str:
        return self._config.get('socks_host', '')

    def get_what_to_do_on_security_violation(self):
        return self._config.get('on_security_violation', '')

    def get_health_checks(self) -> list:
        return self._healthchecks

    def get_checksum_files(self) -> dict:
        return self._config.get('checksum_files', [])

    def get_ssh(self) -> SSH:
        return self._ssh

    def get_notifier(self) -> Notifier:
        return self._notifier

    def set_notifier(self, notifier: Notifier):
        if self._notifier:
            raise Exception('Cannot overwrite notifier')

        self._notifier = notifier

    def is_verify_ssh_fingerprint(self):
        return self._config['verify_ssh_fingerprint']

    def has_active_security_violation(self) -> bool:
        return self._active_security_violation

    def set_active_security_violation_marking(self, is_active: bool):
        self._active_security_violation = is_active

    def set_healthy(self, healthy: bool):

        if not self._healthy and healthy:
            self.get_notifier().is_healthy_again()

        self._healthy = healthy

    def is_healthy(self) -> bool:
        return self._healthy

    def __repr__(self):
        return 'Node <' + self.get_user() + '@' + self.get_address() + ':' + str(self.get_port()) + '>'

    def execute_command(self, *args, **kwargs):
        try:
            return self.get_ssh().execute_command(*args, **kwargs)

        except BadHostKeyException as e:
            self.get_notifier().ssh_identity_possibly_changed()
            raise e

        except Exception as e:
            self.get_notifier().ssh_connection_error(str(e))
            raise e
