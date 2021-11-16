# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Calvin Remsburg (@cremsburg) <cremsburg@protonmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback


class Response(object):

    def __init__(self, resp, info):
        self.body = None
        if resp:
            self.body = resp.read()
        self.info = info

    @property
    def json(self):
        if not self.body:
            if "body" in self.info:
                return json.loads(to_text(self.info["body"]))
            return None
        try:
            return json.loads(to_text(self.body))
        except ValueError:
            return None

    @property
    def status_code(self):
        return self.info["status"]


class LoginHelper:

    def __init__(self, module):
        self.module = module
        self.server = module.params.get('server')
        self.validate_certs = module.params.get('validate_certs', True)
        self.baseurl = f'https://{self.server}'
        self.timeout = module.params.get('timeout', 30)
        self.username = module.params.get('username')
        self.password = module.params.get('password')
        self.headers = {'Content-type': 'application/json'}

    def _url_builder(self, path):
        if path[0] == '/':
            path = path[1:]
        return f'{self.baseurl}/{path}'

    def send(self, method, path, data=None):
        url = self._url_builder(path)
        data = self.module.jsonify(data)

        resp, info = fetch_url(self.module,
                               url,
                               data=data,
                               headers=self.headers,
                               method=method,
                               timeout=self.timeout)

        return Response(resp, info)

    def post(self, path, data=None):
        return self.send('POST', path, data)


    @staticmethod
    def login_spec():
        return dict(
            username=dict(
                required=True,
                fallback=(env_fallback, ['SDCLOUD_USERNAME', 'SDCLOUD_USER']),
                type='str'
            ),
            password=dict(
                required=True,
                fallback=(env_fallback, ['SDCLOUD_PASSWORD', 'SDCLOUD_PASS']),
                no_log=True,
                type='str'
            ),
            scope_id=dict(
                required=True,
                fallback=(env_fallback, ['SDCLOUD_SCOPE_ID', 'SDCLOUD_TENANT_ID']),
                type='str'
            ),
            server=dict(
                required=True,
                fallback=(env_fallback, ['SDCLOUD_URL', 'SDCLOUD_SERVER']),
                type='str'
            ),
            validate_certs=dict(
                type='bool',
                required=False,
                default=True
            ),

        )

class SDCloudHelper:

    def __init__(self, module):
        self.module = module
        self.server = module.params.get('server')
        self.validate_certs = module.params.get('validate_certs', True)
        self.baseurl = f'https://{self.server}'
        self.timeout = module.params.get('timeout', 30)
        self.api_token = module.params.get('api_token')
        self.headers = {'x-iam-token': f'{self.api_token}',
                        'Content-type': 'application/json'}

        # Check if api_token is valid or not by testing the blueprints url
        response = self.get('devicemodel/device-view')
        if response.status_code == 401:
            self.module.fail_json(msg='Failed to login using API token, please verify validity of API token.')

    def _url_builder(self, path):
        if path[0] == '/':
            path = path[1:]
        return f'{self.baseurl}/{path}'

    def send(self, method, path, data=None):
        url = self._url_builder(path)
        data = self.module.jsonify(data)

        resp, info = fetch_url(self.module,
                               url,
                               data=data,
                               headers=self.headers,
                               method=method,
                               timeout=self.timeout)

        return Response(resp, info)

    def get(self, path, data=None):
        return self.send('GET', path, data)

    def put(self, path, data=None):
        return self.send('PUT', path, data)

    def post(self, path, data=None):
        return self.send('POST', path, data)

    def delete(self, path, data=None):
        return self.send('DELETE', path, data)

    @staticmethod
    def ztp_spec():
        return dict(
            api_token=dict(
                required=True,
                fallback=(env_fallback, ['SDCLOUD_API_TOKEN', 'SDCLOUD_API_TOKEN', 'API_TOKEN']),
                no_log=True,
                type='str'
            ),
            root_pwd=dict(
                required=False,
                type='str'
            ),
            serial=dict(
                required=False,
                type='str'
            ),
            server=dict(
                required=False,
                fallback=(env_fallback, ['SDCLOUD_URL', 'SDCLOUD_SERVER']),
                type='str'
            ),
            state=dict(
                required=True,
                choices=['absent', 'present'],
                type='str'
            ),
            validate_certs=dict(
                type='bool',
                required=False,
                default=True
            ),
        )

    @staticmethod
    def device_spec():
        return dict(
            api_token=dict(
                required=True,
                fallback=(env_fallback, ['SDCLOUD_API_TOKEN', 'SDCLOUD_API_TOKEN', 'API_TOKEN']),
                no_log=True,
                type='str'
            ),
            cluster_type=dict(
                required=True,
                choices=['CHASSIS_CLUSTER', 'STANDALONE', 'cluster', 'standalone'],
                type='str'
            ),
            host_name=dict(
                required=False,
                type='str'
            ),
            server=dict(
                required=False,
                fallback=(env_fallback, ['SDCLOUD_URL', 'SDCLOUD_SERVER']),
                type='str'
            ),
            state=dict(
                required=True,
                choices=['absent', 'present'],
                type='str'
            ),
            validate_certs=dict(
                type='bool',
                required=False,
                default=False
            ),
        )
