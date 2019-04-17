
import unittest
import sys
import os
import inspect
import mock
from paramiko.ssh_exception import SSHException, BadHostKeyException

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.entity.host import Node

# for static analysis
if False:
    from ..sshserveraudit.entity.host import Node


class TestNodeEntity(unittest.TestCase):
    def test_execute_command_invokes_ssh_identity_possibly_changed_notification(self):
        """
        When a BadHostKeyException, THEN we send "ssh_identity_possibly_changed" notification
        """

        ssh = mock.Mock()
        ssh.execute_command.side_effect = BadHostKeyException('test', mock.Mock(), mock.Mock())

        notifier = mock.Mock()

        node = Node({'healthchecks': []}, {}, ssh)
        node.set_notifier(notifier)

        try:
            node.execute_command('curl https://iwa-ait.org')
        except BadHostKeyException:
            notifier.ssh_identity_possibly_changed.assert_called_once()
            return

        self.fail('BadHostKeyException not thrown')

    def test_execute_command_invokes_ssh_connection_error(self):
        """
        When got any unknown exception, THEN assume it's a SSH connection fault
        """

        ssh = mock.Mock()
        ssh.execute_command.side_effect = Exception('Shit happened to the SSH connection')

        notifier = mock.Mock()

        node = Node({'healthchecks': []}, {}, ssh)
        node.set_notifier(notifier)

        try:
            node.execute_command('curl https://iwa-ait.org')
        except Exception:
            notifier.ssh_connection_error.assert_called_once()
            return

        self.fail('Exception not thrown')

    def test_set_healthy(self):
        """
        Test that set_healthy() invokes a "is_healthy_again" notification if the health checks are green again
        """

        notifier = mock.Mock()

        node = Node({'healthchecks': []}, {}, mock.Mock())
        node.set_notifier(notifier)

        # set as unhealthy
        node.set_healthy(False)

        # set as healthy and expect a notification
        node.set_healthy(True)
        notifier.is_healthy_again.assert_called_once()

    def test_repr(self):
        """
        Check if the to string casting shows important informations and does not show passwords
        """

        node = Node(
            {
                'healthchecks': [],
                'host': 'iwa-ait.org',
                'port': 22,
                'user': 'adm-technical',
                'password': 'oh-some-secret'
            },
            {},
            mock.Mock()
        )

        self.assertIn('iwa-ait.org', str(node))
        self.assertIn('22', str(node))
        self.assertIn('adm-technical', str(node))
        self.assertNotIn('oh-some-secret', str(node))

    def test_health_checks_constructed(self):
        """
        Verify if health check objects were created
        """

        node = Node(
            {
                'healthchecks': [
                    {
                        'command': '/some/basic/example',
                        'on_failure': None,
                        'on_failure_even_if_security_violation': False
                    },

                    {
                        'command': '/some/basic/example',
                        'on_failure': '/some/rescue-command',
                        'on_failure_even_if_security_violation': True
                    },

                    {
                        'command': '/some/basic/example'
                    }
                ]
            },
            {},
            mock.Mock()
        )

        self.assertEqual(3, len(node.get_health_checks()))
