
from ..entity.host import Node
from ..entity.host import Healthcheck
from ..valueobject.validator import ValidatorResult
from . import Validator


class HealthValidator(Validator):

    @staticmethod
    def is_valid(node: Node) -> ValidatorResult:

        at_least_one_failed = False
        reason = ''
        rescue_commands = []

        for check in node.get_health_checks():
            check = check  # type: Healthcheck
            stdin, stdout, stderr = node.get_ssh().execute_command(check.get_command() + ' > /dev/null 2>&1; echo $?')

            exit_code = int(stdout.read().decode('utf-8'))

            if exit_code > 0:
                at_least_one_failed = True

                if check.get_on_failure():
                    rescue_commands.append(check.get_on_failure())

                reason += check.get_command() + " returned a non-zero status code\n"

        return ValidatorResult(
            not at_least_one_failed,
            reason if reason else 'OK',
            rescue_commands
        )
