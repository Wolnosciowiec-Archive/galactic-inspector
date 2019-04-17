
import unittest
import sys
import os
import inspect
import mock

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.validator.health import HealthValidator

# for static analysis
if False:
    from ..sshserveraudit.validator.health import HealthValidator


class TestHealthValidator(unittest.TestCase):
    def test_validate(self):
        ssh = mock.Mock()
        ssh.configure_mock(**{
            'execute_command.return_value': ''
        })

        health_check = mock.Mock()
        health_check.configure_mock(**{'get_command': 'curl https://iwa-ait.org'})

        node = mock.Mock()
        node.configure_mock(**{
            'get_health_checks.return_value': []
        })

        validator = HealthValidator()
        validator.is_valid(node, force=True)
