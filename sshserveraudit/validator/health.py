
from ..entity.host import Node
from ..entity.host import Healthcheck
from ..valueobject.validator import ValidatorResult
from . import Validator


class HealthValidator(Validator):

    def _is_valid(self, node: Node) -> ValidatorResult:

        at_least_one_failed = False
        reason = ''
        rescue_commands = []

        for check in node.get_health_checks():
            check = check  # type: Healthcheck
            stdin, stdout, stderr = node.execute_command(check.get_command() + ' > /dev/null 2>&1; echo $?')

            exit_code = int(stdout.read().decode('utf-8'))

            if exit_code > 0:
                node.get_notifier().health_check_failed(str(check))

                at_least_one_failed = True
                rescue_command = check.get_on_failure(node.has_active_security_violation())

                if rescue_command:
                    rescue_commands.append(rescue_command)

                reason += check.get_command() + " returned a non-zero status code\n"

        return ValidatorResult(
            not at_least_one_failed,
            reason if reason else 'OK',
            rescue_commands
        )
