
import paramiko
from ..exception import InvalidSumResultException
import socks
import base64
import random
import tornado.log
import paramiko.ssh_exception
import time


class SSH:
    """ SSH wrapper with support for checksum of remote files, logging and reconnection on failure """

    _client = None  # type: paramiko.SSHClient
    _connection_specification = {}
    _lock = None

    def __init__(self,
                 host: str,
                 port: int,
                 key_filename: str,
                 passphrase: str,
                 username: str,
                 password: str,
                 socks_host: str,
                 socks_port: str,
                 verify_ssh_fingerprint: bool,
                 tcp_timeout: int,
                 banner_timeout: int,
                 auth_timeout: int):

        self._connection_specification = {
            'host': host,
            'port': port,
            'key_filename': key_filename,
            'passphrase': passphrase,
            'username': username,
            'password': password,
            'socks_host': socks_host,
            'socks_port': socks_port,
            'verify_ssh_fingerprint': verify_ssh_fingerprint,
            'tcp_timeout': tcp_timeout,
            'banner_timeout': banner_timeout,
            'auth_timeout': auth_timeout
        }

    @staticmethod
    def _generate_command(command: str):
        rand = random.randint(1, 4)
        encoded = base64.b64encode(command.encode('utf-8')).decode('utf-8')

        if rand == 1:
            return '/bin/sh -c "' + SSH._quote(command) + '"'
        elif rand == 2:
            return 'sh -c "$(eval \'echo \"' + encoded + '\"|base64 -d\')"'
        elif rand == 3:
            return '/bin/bash --init-file /dev/null -c "/bin/sh -c \'' + SSH._quote(command) + '\'"'
        else:
            return command

    @staticmethod
    def _quote(command: str):
        return command.replace('"', '\"')

    def get_file_hash(self, path: str, sum_method: str) -> str:
        """
        Get remote file HASH using the checksum method specified in `sum_method` parameter

        Example:
        ```
            get_file_hash('/bin/bash', 'sha256sum')
        ```

        :param path:
        :param sum_method:
        :return:
        """

        command = self._generate_command(sum_method + ' "' + path + '"')
        stdin, stdout, stderr = self.execute_command(command)
        out = stdout.read().decode('utf-8')
        parts = out.replace('  ', ' ').split(' ')

        if len(parts) < 2:
            raise InvalidSumResultException('Sum method returned an invalid value')

        return parts[0]

    def execute_command(self, command: str, retry_num: int = 1, max_retry_num: int = 4) -> tuple:
        """
        Execute a remote command, with N-attempts in case of connection failure
        (this method should be fault tolerant when using SOCKS proxy with eg. TOR network)

        :param command:
        :param retry_num:
        :param max_retry_num:
        :return:
        """

        tornado.log.app_log.info('(retry ' + str(retry_num) + '/' + str(max_retry_num) + ') ' + command)

        if retry_num < max_retry_num:
            try:
                return self._execute_command(force=retry_num > 1, command=command)
            except paramiko.ssh_exception.SSHException:
                pass
            except AttributeError:
                pass
            except socks.ProxyError:
                pass
            except EOFError:
                pass

            time.sleep(0.5)
            return self.execute_command(command, retry_num + 1, max_retry_num)

        elif retry_num == max_retry_num:
            return self._execute_command(force=retry_num > 1, command=command)

    def _execute_command(self, command: str, force: bool) -> tuple:
        return self._get_client(force=force).exec_command(command, timeout=30)

    def _create_client(self):
        # do not create parallel clients, let one thread wait for another
        if self._lock:
            tornado.log.app_log.info('SSH client locked, waiting for lock release')

            while self._lock and (self._lock + 10) > time.time():
                time.sleep(1)

            self._lock = None
            self._create_client()
            return None

        sock = self._create_socks_proxy()

        self._lock = time.time()
        tornado.log.app_log.info('SSH client locked at ' + str(self._lock))

        self._client = paramiko.SSHClient()
        self._client.get_transport()

        # this is strongly insecure, but should be allowed for TEST environments
        if not self._connection_specification['verify_ssh_fingerprint']:
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self._client.load_system_host_keys()

        self._client.connect(
            self._connection_specification['host'],
            port=self._connection_specification['port'],
            timeout=self._connection_specification['tcp_timeout'],
            auth_timeout=self._connection_specification['auth_timeout'],
            banner_timeout=self._connection_specification['banner_timeout'],
            key_filename=self._connection_specification['key_filename'] if self._connection_specification['key_filename'] else None,
            passphrase=self._connection_specification['passphrase'] if self._connection_specification['passphrase'] else None,
            username=self._connection_specification['username'],
            password=self._connection_specification['password'],
            sock=sock
        )

        self._lock = None

    def _create_socks_proxy(self):
        if not self._connection_specification['socks_host'] or not self._connection_specification['socks_port']:
            return None

        tornado.log.app_log.info(
            'Using SOCKS proxy ' + str(self._connection_specification['socks_host']) + ':' +
            str(self._connection_specification['socks_port'])
        )

        sock = socks.socksocket()
        sock.set_proxy(
            proxy_type=socks.SOCKS5,
            addr=self._connection_specification['socks_host'],
            port=self._connection_specification['socks_port'],
        )
        sock.connect((self._connection_specification['host'], self._connection_specification['port']))

        return sock

    def _get_client(self, force=False):
        if not self._client or force:
            self._client = None
            self._create_client()

        return self._client
