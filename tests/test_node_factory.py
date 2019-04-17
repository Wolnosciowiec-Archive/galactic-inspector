
import unittest
import sys
import os
import inspect

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/../'
sys.path.append(path)
from sshserveraudit.factory.node import NodeFactory

# for static analysis
if False:
    from ..sshserveraudit.factory.node import NodeFactory


class TestNodeFactory(unittest.TestCase):
    def test_node_factory_adds_notifier(self):
        """
        Check if NodeFactory does properly inject a Notifier instance
        and by the way check if the other attributes are injected with a KeyError
        """

        factory = NodeFactory()
        node = factory.create(
            {
                'host': 'riotkit.org',
                'public_key': 'some',
                'port': 22,
                'passphrase': 'fck-rich-pigs',
                'user': 'acab',
                'password': '1312',
                'notifications': {
                    'type': 'none'
                },
                'healthchecks': []
            },
            {}
        )

        self.assertIsNotNone(node.get_notifier())
