
from ..entity.host import Node
from ..valueobject.validator import ValidatorResult
import time
import tornado.log


class Validator:
    max_cache_time = 120.0

    # static
    cache = {}

    def _get_cache_ident(self, node: Node):
        return str(node) + '_' + str(type(self).__name__)

    def _cache_results(self, result: ValidatorResult, node: Node) -> ValidatorResult:
        Validator.cache[self._get_cache_ident(node)] = {
            'result': result,
            'created_at': time.time()
        }

        tornado.log.app_log.info('Cache created')

        return Validator.cache[self._get_cache_ident(node)]['result']

    def _get_results_from_cache(self, node: Node):
        ident = self._get_cache_ident(node)

        if ident not in Validator.cache:
            tornado.log.app_log.info('Cache not found')
            return None

        cached = Validator.cache[ident]

        if not cached['result'] or time.time() >= (cached['created_at'] + self.max_cache_time):
            tornado.log.app_log.info('Cache expired')

            del Validator.cache[ident]
            return None

        return cached['result']

    def is_valid(self, node: Node, force=False, only_cache=False) -> ValidatorResult:
        results = self._get_results_from_cache(node)

        if only_cache and not results:
            return ValidatorResult(False, 'Status not ready, waiting for check to be performed...', [])

        if results and not force:
            return results

        return self._cache_results(self._is_valid(node), node)

    def _is_valid(self, node: Node) -> ValidatorResult:
        pass
