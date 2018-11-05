
from .authenticity import AuthenticityCheckLoopController
from .healthcheck import HealthCheckLoopController
from .abstract import AbstractLoopController
from ..entity.host import Node
from time import sleep
import threading
import tornado.log
import traceback
import sys


class ShellController:
    threads = []                    # type: list[threading.Thread]
    nodes = {}                      # type: dict[Node]
    sleep_time = 30                 # type: int
    controllers = []                # type:

    def __init__(self, nodes: dict, sleep_time: int):
        self.nodes = nodes
        self.sleep_time = sleep_time
        self.controllers = [
            AuthenticityCheckLoopController,
            HealthCheckLoopController
        ]

    def start(self):
        for node_name, node in self.nodes.items():
            self._spawn_thread_for_node(node)
            sleep(1)

    def _spawn_thread_for_node(self, node: Node):
        self._create_thread(self._create_worker_loop, [node])

    def _create_worker_loop(self, node: Node):
        while True:
            for controller in self.controllers:
                try:
                    controller.perform_check(node)

                except Exception as e:
                    tornado.log.app_log.warning(
                        'Audit check was interrupted for node ' + str(node) + ' because of an error'
                    )

                    tornado.log.app_log.error('[' + str(node) + '] ' + str(e))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)

            sleep(self.sleep_time)

    def _create_thread(self, target, args):
        healthcheck_thread = threading.Thread(target=target, args=args)
        healthcheck_thread.daemon = True
        healthcheck_thread.start()
        self.threads.append(healthcheck_thread)
