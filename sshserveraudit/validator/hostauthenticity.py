
from ..entity.host import Node
from ..valueobject.validator import ValidatorResult
from ..exception import InvalidSumResultException
from . import Validator


class HostAuthenticityValidator(Validator):
    @staticmethod
    def is_valid(node: Node) -> ValidatorResult:
        code = True
        reason = ''
        results = HostAuthenticityValidator.validate(node)

        for name, generated_hash in results.items():
            if node.get_expected_checksum(name) != generated_hash:
                code = False
                reason = 'Expectation failed for "' + name + '"'

        return ValidatorResult(code, reason, [])

    @staticmethod
    def build_expectations(volume: Node) -> dict:
        return HostAuthenticityValidator.validate(volume)

    @staticmethod
    def validate(node: Node) -> dict:
        results = {}

        for name, path in node.get_checksum_files().items():
            try:
                generated_hash = node.get_ssh().get_file_hash(path, node.get_checksum_method())
            except InvalidSumResultException:
                generated_hash = ''

            results[name] = generated_hash

        return results
