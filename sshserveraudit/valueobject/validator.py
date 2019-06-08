

class ValidatorResult:
    status = False
    message = ''
    rescue_commands = []
    last_check_time = 'unknown'

    def __init__(self, status: bool, message: str, rescue_commands: list):
        self.status = status
        self.message = message
        self.rescue_commands = rescue_commands

    def is_ok(self) -> bool:
        return self.status

    def get_message(self) -> str:
        return self.message

    def get_rescue_commands(self) -> list:
        return self.rescue_commands

    def inject_last_check_time(self, last_check_time: str):
        self.last_check_time = last_check_time

        return self

    def to_dict(self, node_name: str, check_name: str):
        return {
            'ident': node_name + '_' + check_name + '=' + str(self.status),
            'status': self.status,
            'message': self.message if self.message else 'OK',
            'lastCheckTime': self.last_check_time
        }
