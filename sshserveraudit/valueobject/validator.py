

class ValidatorResult:
    status = False
    message = ''
    rescue_commands = []

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

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message if self.message else 'OK'
        }
