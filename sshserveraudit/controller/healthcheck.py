
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
                tornado.log.app_log.error('!!! [' + str(node) + '][Healthcheck] Attempting to execute ' +
                                          ' rescue command "' + str(command) + "")

                try:
                    stdin, stdout, stderr = node.execute_command(command + ' > /dev/null 2>&1; echo $?')
                    exit_code = int(stdout.read().decode('utf-8'))

                    if exit_code > 0:
                        raise Exception('Rescue command failed, exit code is ' + str(exit_code))

                except Exception as e:
                    tornado.log.app_log.error('!!! [' + str(node) + '][Healthcheck] Cannot execute rescue command "' + command + '"')
                    tornado.log.app_log.error(str(e))

                    node.get_notifier().tried_to_recover_after_health_check(command, str(e))

            node.set_healthy(False)
            return False

        tornado.log.app_log.info('[' + str(node) + '][Healthcheck] Looks OK')
        node.set_healthy(True)

        return True
