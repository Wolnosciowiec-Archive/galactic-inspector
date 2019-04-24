
import requests
import json
import hashlib
from time import time as get_current_time
from time import sleep


class Notifier:
    node = None
    _archive = {}
    _resend_after = 120

    def __init__(self, config: dict, node):
        self.node = node

    def health_check_failed(self, check_name: str):
        pass

    def authenticity_check_failed(self, details: dict):
        pass

    def tried_to_recover_after_health_check(self, rescue_cmd: str, output: str):
        pass

    def ssh_identity_possibly_changed(self):
        pass

    def ssh_connection_error(self, details: str):
        pass

    def is_healthy_again(self):
        pass

    def authenticity_executed_prevention_command(self, details: str):
        pass

    def _get_msg_id(self, msg: str):
        h = hashlib.new('sha256')
        h.update(msg.encode('utf-8'))

        return h.hexdigest()

    def _should_send_notification(self, msg: str) -> bool:
        msg_id = self._get_msg_id(msg)

        if msg_id in self._archive:
            if (self._archive[msg_id]['time'] + self._resend_after) <= get_current_time():
                del self._archive[msg_id]
                return True

            return False

        return True

    def _store(self, msg: str):
        msg_id = self._get_msg_id(msg)
        self._archive[msg_id] = {
            'time': get_current_time(),
            'msg': msg
        }


class SlackNotifier(Notifier):
    url = ""
    _proxy = ""
    _timeout = 300

    def __init__(self, config: dict, node):
        super().__init__(config, node)
        self.url = config['url']
        self._resend_after = int(config.get('resend_after', 600))
        self._proxy = str(config.get('proxy', ''))
        self._proxy_retry_num = int(config.get('proxy_retry_num', 3))
        self._proxy_fallback_on_failure = config.get('proxy_fallback_on_failure', False)
        self._timeout = int(config.get('connection_timeout', 300))

    def health_check_failed(self, check_name: str):
        self._send(":exclamation: :exclamation: :exclamation: " +
                   "Health check `" + str(check_name) + "` failed at `" + str(self.node) + "`")

    def tried_to_recover_after_health_check(self, rescue_cmd: str, output: str):
        self._send(":bangbang: Cannot perform recovery after health check detected the failure. " +
                   "Tried resuce command `" + str(rescue_cmd) + "`, got `" + str(output) + "`")

    def ssh_identity_possibly_changed(self):
        self._send(":suspect: :bangbang: Cannot connect to SSH, it looks that possibly " +
                   " the fingerprint may be changed. Watch out for Man-In-The-Middle attacks.")

    def authenticity_check_failed(self, details: dict):
        self._send(":suspect: :bangbang: Cannot prove that the host is authentic, details: `" + str(details) + "`")

    def authenticity_executed_prevention_command(self, details: str):
        self._send(":suspect: :warning: Attempting to execute a prevention command, details: `" + str(details) + "`")

    def ssh_connection_error(self, details: str):
        self._send(":warning: SSH connection error: `" + str(details) + "`")

    def is_healthy_again(self):
        self._send(":white_check_mark: All health checks are now passing on `" + str(self.node) + "`")

    def _get_proxy(self, retry_num: int = 0):
        # If socks proxy is still failing, then send the notification without the proxy
        # (if policy defines that fallback on failure is allowed)
        if self._proxy_fallback_on_failure and self._proxy_retry_num and retry_num >= self._proxy_retry_num:
            return None

        if self._proxy:
            return self._proxy

        return None

    def _send(self, msg: str, retry_num: int = 0):
        if not self._should_send_notification(msg):
            return

        try:
            response = requests.post(
                self.url, data=json.dumps({'text': msg}),
                headers={'Content-Type': 'application/json'},
                proxies=self._get_proxy(retry_num),
                timeout=self._timeout
            )
            if response.status_code != 200:
                raise ValueError(
                    'Request to slack returned an error %s, the response is:\n%s'
                    % (response.status_code, response.text)
                )
        except Exception as e:
            if self._proxy_retry_num and retry_num < self._proxy_retry_num:
                self._send(msg, retry_num + 1)
                sleep(1)
                return

            raise e

        self._store(msg)
