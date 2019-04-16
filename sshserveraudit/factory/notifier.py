
from ..service.notify import *


class NotifierFactory:
    _types = {
        'slack': SlackNotifier,
        'mattermost': SlackNotifier,
        'none': Notifier
    }

    @staticmethod
    def create(spec: dict, node) -> Notifier:
        selected_type = spec.get('type', 'none')

        if selected_type not in NotifierFactory._types:
            raise Exception('Configuration error: Notification type is invalid. ' +
                            'Allowed values: ' + str(NotifierFactory._types))

        return NotifierFactory._types[selected_type](spec, node)
