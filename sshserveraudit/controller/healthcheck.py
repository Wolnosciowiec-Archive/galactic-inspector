
from ..validator.health import HealthValidator
from ..entity.host import Node
from .abstract import AbstractLoopController
import tornado.log


class HealthCheckLoopController(AbstractLoopController):
    @staticmethod
    def perform_check(node: Node):
        """ Monitor and react on failure """

        tornado.log.app_log.info('[' + str(node) + '][Healthcheck] Performing a check')
        result = HealthValidator.is_valid(node)

        if not result.is_ok():
            tornado.log.app_log.error('!!! [' + str(node) + '][Healthcheck] At least one of health checks failed')

            for command in result.get_rescue_commands():
                try:
                    node.get_ssh().execute_command(command)

                except Exception as e:
                    tornado.log.app_log.error('!!! [' + str(node) + '][Healthcheck] Cannot execute rescue command "' + command + '"')
                    tornado.log.app_log.error(str(e))

            return

        tornado.log.app_log.info('[' + str(node) + '][Healthcheck] Looks OK')
