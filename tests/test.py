
import json
import os

if __name__ == '__main__':
    from.HttpTestCase import HttpTestCase
else:
    from HttpTestCase import HttpTestCase


class TestDeployerController(HttpTestCase):

    def test_deploy_with_valid_token(self):
        response = self.fetch('/deploy/test?token=123')
        self.assertEqual(response.code, 202)
        self.assertIn('# Deployment started: test', str(response.body))
        self.assertIn('home', str(response.body))

    def test_deploy_with_valid_token_and_provided_variable(self):
        response = self.fetch('/deploy/test?token=123&dir=' + os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(response.code, 202)
        self.assertIn('test_HelloController.py', str(response.body))

    def test_escapes_arguments_properly(self):
        response = self.fetch('/deploy/test?token=123&dir=\'&&/bin/bash')
        self.assertEqual(response.code, 500)

    def test_will_not_deploy_if_token_not_valid(self):
        response = self.fetch('/deploy/test?token=not-valid')
        self.assertEqual(response.code, 403)

        data = json.loads(response.body.decode('utf-8'))

        self.assertNotIn('output', data)
        self.assertIn('message', data)
        self.assertIn('serviceName', data)

    def test_will_not_deploy_if_service_does_not_exists(self):
        response = self.fetch('/deploy/no-such-service')
        self.assertEqual(response.code, 404)

    def test_deploy_with_post_method_and_header_authorization(self):
        response = self.fetch(path='/deploy/test', method='POST', headers={'X-Auth-Token': '123'}, body='')
        self.assertEqual(response.code, 202)

    def test_deploy_only_if_request_body_matches_a_regexp(self):
        response = self.fetch(
            path='/deploy/test_regexp',
            method='POST',
            headers={'X-Auth-Token': '456'},
            body='{"branch": "production"}'
        )

        self.assertEqual(response.code, 202)

    def test_not_deploy_if_request_body_does_not_match_the_regexp_but_has_valid_token_and_service_name(self):
        response = self.fetch(
            path='/deploy/test_regexp',
            method='POST',
            headers={'X-Auth-Token': '456'},
            body='{"branch": "not-considered-branch-by-regexp"}'
        )

        data = json.loads(response.body.decode('utf-8'))

        self.assertEqual(response.code, 200)
        self.assertEqual('Request validation returned a status that there is no need to deploy', data['output'])
