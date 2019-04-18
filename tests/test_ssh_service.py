
import unittest
import sys
import os
import inspect
import mock
from io import BytesIO

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.service.ssh import SSH
from sshserveraudit.exception import InvalidSumResultException

# for static analysis
if False:
    from ..sshserveraudit.service.ssh import SSH
    from ..sshserveraudit.exception import InvalidSumResultException


class TestSshService(unittest.TestCase):

    def test_get_file_hash(self):
        """
        Happy path
        """

        ssh = self._create_ssh_instance()

        stdin = BytesIO()
        stdout = BytesIO()
        stdout.write(b'a167c8c1644da234b6fe5e240baff187a11d966ff94dea71c3c97ec597307390  /etc/resolv.conf')
        stdout.seek(0)
        stderr = BytesIO()

        with mock.patch.object(ssh, '_execute_command', return_value=(stdin, stdout, stderr)):
            self.assertEqual(
                'a167c8c1644da234b6fe5e240baff187a11d966ff94dea71c3c97ec597307390',
                ssh.get_file_hash('/tmp/some-file', 'sha256')
            )

    def test_get_file_hash_reports_invalid_format(self):
        """
        get_file_hash() should throw an exception, if the hash cannot be extracted
        """

        ssh = self._create_ssh_instance()

        stdin = BytesIO()
        stdout = BytesIO()
        stdout.write(b'a167c8c1644da234b6fe5e240baff187a11d966ff94dea71c3c97ec597307390')
        stdout.seek(0)
        stderr = BytesIO()

        with mock.patch.object(ssh, '_execute_command', return_value=(stdin, stdout, stderr)):
            try:
                ssh.get_file_hash('/tmp/some-file', 'sha256')
            except InvalidSumResultException:
                self.assertRaises(InvalidSumResultException)
                return

            self.fail('Expected a exception to be raised')

    def test_retries_command_until_success(self):
        """
        Verify that the execute_command() will attempt multiple retries until the task will not be done
        """

        ssh = self._create_ssh_instance()

        stdin = BytesIO()
        stdout = BytesIO()
        stdout.write(b'something')
        stdout.seek(0)
        stderr = BytesIO()

        with mock.patch.object(ssh, '_execute_command') as mocked_exec:
            mocked_exec.side_effect = [
                AttributeError('Next please'),
                AttributeError('Next please'),
                (stdin, stdout, stderr)
            ]

            r_in, r_out, r_err = ssh.execute_command('ls -la', retry_num=1, max_retry_num=3)

            self.assertEqual('something', r_out.read().decode('utf-8'))

    def test_retries_command_until_error(self):
        """
        Check that execute_command() will raise an exception after all retries
        """

        ssh = self._create_ssh_instance()

        with mock.patch.object(ssh, '_execute_command') as mocked_exec:
            mocked_exec.side_effect = [
                AttributeError('Next please'),
                AttributeError('Next please')
            ]

            try:
                ssh.execute_command('ls -la', retry_num=1, max_retry_num=2)
            except AttributeError:
                self.assertRaises(AttributeError)
                return

            self.fail('Expected that the AttributeError will be thrown')

    @staticmethod
    def _create_ssh_instance() -> SSH:
        return SSH(
            host='localhost',
            port=22,
            key_filename='/tmp/some-key-file',
            passphrase='key-passphrase',
            password='some-password',
            username='admin',
            socks_host='tor',
            socks_port='9050',
            verify_ssh_fingerprint=True,
            tcp_timeout=300,
            banner_timeout=300,
            auth_timeout=300
        )
