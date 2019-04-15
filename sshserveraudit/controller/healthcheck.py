
from ..validator.health import HealthValidator
from ..entity.host import Node
from .abstract import AbstractLoopController
import tornado.log


class HealthCheckLoopController(AbstractLoopController):

    validator = None  # type: HealthValidator

    def __init__(self, configured_volumes: dict, validator: HealthValidator):
        super().__init__(configured_volumes)
        self.validator = validator

    def perform_check(self, node: Node) -> bool:
        """ Monitor and react on failure """

        tornado.log.app_log.info('[' + str(node) + '][Healthcheck] Performing a check')
        result = self.validator.is_valid(node=node, force=True)

        if not result.is_ok():
            tornado.log.app_log.error('!!! [' + str(node) + '][Healthcheck] At least one of health checks failed')
            tornado.log.app_log.info(result.get_rescue_commands())

            for command in result.get_rescue_commands():
                try:
                    node.get_ssh().execute_command(command)

                except Exception as e:
                    tornado.log.app_log.error('!!! [' + str(node) + '][Healthcheck] Cannot execute rescue command "' + command + '"')
                    tornado.log.app_log.error(str(e))

            return False

        tornado.log.app_log.info('[' + str(node) + '][Healthcheck] Looks OK')
        return True
