
import unittest
import sys
import os
import inspect
import mock
import time

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.service.notify import SlackNotifier

# for static analysis
if False:
    from ..sshserveraudit.service.notify import SlackNotifier


class TestSlackNotifier(unittest.TestCase):

    def test_is_not_spamming_with_notifications(self):
        notifier = SlackNotifier(
            {
                'type': 'slack',
                'resend_after': 1,
                'url': 'http://some-webhook-url'
            },
            mock.Mock()
        )

        with mock.patch('requests.post') as mocked_response:
            response = mock.Mock()
            response.status_code = 200
            mocked_response.return_value = response

            notifier.is_healthy_again()
            notifier.is_healthy_again()

            time.sleep(1)
            notifier.is_healthy_again()

            self.assertEqual(2, mocked_response.call_count,
                             'Expected that #1st notification will be sent, ' +
                             '#2nd not - because it\'s too fast (resend_after = 1 sec), #3rd should be sent')

