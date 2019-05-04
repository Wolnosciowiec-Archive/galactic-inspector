
import unittest
import sys
import os
import inspect
import mock

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.validator.hostauthenticity import HostAuthenticityValidator

# for static analysis
if False:
    from ..sshserveraudit.validator.hostauthenticity import HostAuthenticityValidator


class TestHostAuthenticityValidator(unittest.TestCase):
    def test_validate(self):
        validator = HostAuthenticityValidator(120)

        self.assertEqual(
            {'some-name': 'some-hash-there'},
            validator.build_expectations(self._create_test_node('some-hash-there'))
        )

    def test_is_valid_invalid(self):
        validator = HostAuthenticityValidator(120)
        node = self._create_test_node('some-hash-here', {
            'get_expected_checksum.return_value': 'different-hash-expected'
        })

        results = validator.is_valid(node, force=False)

        node.set_active_security_violation_marking.assert_called_once_with(True)
        self.assertFalse(results.is_ok())

    def test_is_valid(self):
        validator = HostAuthenticityValidator(120)
        node = self._create_test_node('some-hash-here', {
            'get_expected_checksum.return_value': 'some-hash-here'
        })

        results = validator.is_valid(node, force=False)

        node.set_active_security_violation_marking.assert_called_once_with(False)
        self.assertTrue(results.is_ok())

    @staticmethod
    def _create_test_node(hash_returned_from_server, configuration={}):
        ssh = mock.Mock()
        ssh.configure_mock(**{
            'get_file_hash.return_value': hash_returned_from_server
        })

        node = mock.Mock()
        node.configure_mock(**{**{
            'get_checksum_files.return_value': {
                'some-name': '/some/path'
            },
            'get_checksum_method.return_value': 'sha256sum',
            'get_ssh.return_value': ssh
        }, **configuration})

        return node
