
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

            if node.get_what_to_do_on_security_violation() and node.should_take_action_on_security_violation():

                # execute a "rescue/notify command", mark as executed
                node.set_command_executed_on_current_violation(True)
                node.execute_command(node.get_what_to_do_on_security_violation())

                # log, notify
                tornado.log.app_log.error('!!! [' + str(node) + '][Authenticity] Executing prevention command')
                node.get_notifier().authenticity_executed_prevention_command(
                    str(node.get_what_to_do_on_security_violation())
                )

            return False

        tornado.log.app_log.info('[' + str(node) + '][Authenticity] Looks OK')
        node.set_command_executed_on_current_violation(False)

        return True
