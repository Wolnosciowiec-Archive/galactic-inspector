
from ..entity.host import Node
from ..valueobject.validator import ValidatorResult
import time
import datetime
import tornado.log


class Validator:
    max_cache_time = 120.0

    # static
    cache = {}

    def __init__(self, max_cache_time: int):
        self.max_cache_time = max_cache_time

    def _get_cache_ident(self, node: Node):
        return str(node) + '_' + str(type(self).__name__)

    def _cache_results(self, result: ValidatorResult, node: Node) -> ValidatorResult:
        result.inject_last_check_time(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))

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
            return None, None

        cached = Validator.cache[ident]

        if not cached['result']:
            tornado.log.app_log.info('Cache not warmed up yet...')
            return None, None

        if time.time() >= (cached['created_at'] + self.max_cache_time):
            tornado.log.app_log.info('Cache expired')

        return cached['result'], cached['created_at']

    def is_valid(self, node: Node, force=False, only_cache=False) -> ValidatorResult:
        results, cache_time = self._get_results_from_cache(node)

        if only_cache and not results:
            return ValidatorResult(False, 'Status not ready, waiting for check to be initially performed...', [])

        if results and not force:
            return results

        return self._cache_results(self._is_valid(node), node)

    def _is_valid(self, node: Node) -> ValidatorResult:
        pass
