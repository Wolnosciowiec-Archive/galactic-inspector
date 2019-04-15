
from ..validator.hostauthenticity import HostAuthenticityValidator
from ..entity.host import Node
from .abstract import AbstractLoopController
import tornado.log


class AuthenticityCheckLoopController(AbstractLoopController):

    validator = None  # type: HostAuthenticityValidator

    def __init__(self, configured_nodes: dict, validator: HostAuthenticityValidator):
        super().__init__(configured_nodes)
        self.validator = validator

    def perform_check(self, node: Node) -> bool:
        """ Monitor and react on failure """

        tornado.log.app_log.info('[' + str(node) + '][Authenticity] Performing an authenticity check')
        result = self.validator.is_valid(node=node, force=True)

        if not result.is_ok():
            tornado.log.app_log.error('!!! [' + str(node) + '][Authenticity] Security violation found on node')

            if node.get_what_to_do_on_security_violation():
                tornado.log.app_log.error('!!! [' + str(node) + '][Authenticity] Executing prevention command')
                node.get_ssh().execute_command(node.get_what_to_do_on_security_violation())
            return False

        tornado.log.app_log.info('[' + str(node) + '][Authenticity] Looks OK')
        return True
