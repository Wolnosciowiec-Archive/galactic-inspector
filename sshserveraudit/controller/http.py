from tornado import web

from ..validator.hostauthenticity import HostAuthenticityValidator
from ..validator.health import HealthValidator
from ..validator import Validator
import json


class ValidationHttpController(web.RequestHandler):

    def data_received(self, chunk):
        pass

    def get(self):
        """ Runs each validator on each node """

        node_report = {}
        has_at_least_one_failure = False

        for node_name, node in self.application.configured_nodes.items():
            node_report[node_name] = {}

            for validator_name, validator_module in self.application.get_validators().items():
                validator = validator_module  # type: Validator

                result = validator.is_valid(node, force=False)
                node_report[node_name][validator_name] = result.to_dict()

                if not result.is_ok():
                    has_at_least_one_failure = True

        if has_at_least_one_failure:
            self.set_status(503, 'At least one failure')

        self.write(json.dumps(node_report, sort_keys=True, indent=4))

