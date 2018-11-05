

from ..entity.host import Node
from ..service.ssh import SSH


class NodeFactory:

    @staticmethod
    def create(attributes: dict, expectations: dict) -> Node:
        return Node(attributes, expectations, SSH(
            host=attributes['host'],
            port=attributes['port'],
            key_filename=attributes['public_key'],
            passphrase=attributes['passphrase'],
            username=attributes['user'],
            password=attributes['password'],
            socks_host=attributes['socks_host'],
            socks_port=attributes['socks_port']
        ))
