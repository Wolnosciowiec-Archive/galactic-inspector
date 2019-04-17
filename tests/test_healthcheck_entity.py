
import unittest
import sys
import os
import inspect
from unittest_data_provider import data_provider

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.entity.host import Healthcheck

# for static analysis
if False:
    from ..sshserveraudit.entity.host import Healthcheck


class TestHealthCheckEntity(unittest.TestCase):

    def provide_data():
        return [
            [
                # should execute repair command WHEN security is violated already (eg. host authenticity broken)
                True,

                # is security violation active?
                True,
                # command to execute
                '/usr/bin/some-repair-command'
            ],

            [
                # should execute repair command WHEN security is violated already (eg. host authenticity broken)
                False,

                # is security violation active?
                True,

                # command to execute
                ''
            ],

            [
                # should execute repair command WHEN security is violated already (eg. host authenticity broken)
                True,

                # is security violation active?
                False,

                # command to execute
                '/usr/bin/some-repair-command'
            ]
        ]

    @data_provider(provide_data)
    def test_decision(self, exec_repair_on_sec_violation, security_violation_active, expected_command):
        hc = Healthcheck(
            '/usr/bin/some-monitor-command',
            '/usr/bin/some-repair-command',

            # should execute repair command when there is a security violation active?
            exec_repair_on_sec_violation
        )

        # first argument: Security violation is active
        self.assertEqual(expected_command, hc.get_on_failure(security_violation_active))
