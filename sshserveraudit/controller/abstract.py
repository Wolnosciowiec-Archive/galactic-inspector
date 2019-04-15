
from ..entity.host import Node


class AbstractLoopController:
    configured_nodes = {}  # type: dict[Node]

    def __init__(self, configured_volumes: dict):
        self.configured_nodes = configured_volumes

    @staticmethod
    def perform_check(node: Node) -> bool:
        pass
