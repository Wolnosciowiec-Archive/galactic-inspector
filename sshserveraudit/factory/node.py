

from ..entity.host import Node
from ..service.ssh import SSH
from .notifier import NotifierFactory


class NodeFactory:

    @staticmethod
    def create(attributes: dict, expectations: dict) -> Node:

        ssh = SSH(
            host=attributes['host'],
            port=attributes.get('port', 22),
            key_filename=attributes['public_key'],
            passphrase=attributes['passphrase'],
            username=attributes['user'],
            password=attributes['password'],
            socks_host=attributes.get('socks_host', ''),
            socks_port=attributes.get('socks_port', 9050),
            verify_ssh_fingerprint=attributes.get('verify_ssh_fingerprint', True),
            banner_timeout=attributes.get('ssh_banner_timeout', 300),
            auth_timeout=attributes.get('ssh_auth_timeout', 300),
            tcp_timeout=attributes.get('ssh_tcp_timeout', 300)
        )

        node = Node(attributes, expectations, ssh)
        node.set_notifier(NotifierFactory.create(attributes['notifications'], node))

        return node
