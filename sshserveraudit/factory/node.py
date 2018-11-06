

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
            socks_port=attributes['socks_port'],
            verify_ssh_fingerprint=attributes['verify_ssh_fingerprint'],
            banner_timeout=attributes['ssh_banner_timeout'],
            auth_timeout=attributes['ssh_auth_timeout'],
            tcp_timeout=attributes['ssh_tcp_timeout']
        ))
