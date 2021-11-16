#!/usr/bin/python

# Copyright: (c) 2020, Calvin Remsburg (@cremsburg) <cremsburg@protonmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: login

short_description: Login and retrieve an API token.

version_added: "0.0.1"

description: This module will leverage Security Director Cloud's REST API to automate the login and storing of token.

options:
    username:
        description:
          - used to authenticate to the API
          - falls back to environment variables SDCLOUD_USERNAME and SDCLOUD_USER
        required: true
        type: str
    password:
        description:
          - user's login password
          - PLEASE CONSIDER using environment variables or a vault service
          - falls back to environment variables SDCLOUD_PASSWORD and SDCLOUD_PASS
        required: true
        type: str
    server:
        description:
          - Security Director Cloud URL
          - falls back to environment variables SDCLOUD_URL and SDCLOUD_SERVER
        required: true
        type: str
    validate_certs:
        description:
            - whether or not the certificate is valid
            - may help those behind proxies
        required: false
        default: true
        type: bool

extends_documentation_fragment:
    - cremsburg.sdcloud.login

author:
    - Calvin Remsburg (@cremsburg)
'''

EXAMPLES = r'''
---
### #################################################################
### # LOG INTO SECURITY DIRECTOR CLOUD AND STORE YOUR API TOKEN
### #################################################################
- hosts: localhost
  gather_facts: False
  become: False
  tasks:
    - name: "### LOG INTO SECURITY DIRECTOR CLOUD AND STORE API TOKEN"
      cremsburg.sdcloud.login:

        # define Security Director Cloud parameters
        server: "sdcloud-eap.juniperclouds.net"

        # define user creds
        username: "ABCDEFG123"
        password: "juniper123"

      register: api_token

    - debug:
        var: api_token
'''


from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cremsburg.sdcloud.plugins.module_utils.sdcloud.api import LoginHelper
from ansible.module_utils._text import to_native


def first_login(module, rest):
    # #######################################################################
    # if the user set the state to 'absent', then we need to either delete
    #   an existing device, or report back to the user that the device didn't
    #   exist.
    # #######################################################################
    response = rest.post("iam/authenticate", data={
        "user": {
            "domain": "default",
            "name": module.params['username']
        },
        "password": module.params['password'],
        "methods": [
            "PASSWORD"
        ]
    })

    if response.status_code != 200:
        module.fail_json(msg=f"Expected a 200 status code response from the API, here is the response information to help you debug : {response.info}")

    resources = response.json

    # #######################################################################
    # validate that resources is a dictionary
    # #######################################################################
    if isinstance(resources, dict):
        pass
    else:
        module.fail_json(msg=f"The response returned is not in a dictionary format, contact support \n{resources}")

    return resources


def second_login(module, rest, id_token):
    # #######################################################################
    # if the user set the state to 'absent', then we need to either delete
    #   an existing device, or report back to the user that the device didn't
    #   exist.
    # #######################################################################
    response = rest.post("iam/authenticate", data={
        "token": id_token,
        "scope_id": module.params['scope_id'],
        "methods": [
            "TOKEN"
        ]
    })

    if response.status_code != 200:
        module.fail_json(msg=f"Expected a 200 status code response from the API, here is the response information to help you debug : {response.info}")

    resources = response.json

    # #######################################################################
    # validate that resources is a dictionary
    # #######################################################################
    if isinstance(resources, dict):
        pass
    else:
        module.fail_json(msg=f"The response returned is not in a dictionary format, contact support \n{resources}")

    return resources


def core(module):
    # #######################################################################
    # this is where we take in AnsibleModule class created earlier in the
    # main function, when we inserted our argument spec into it.
    # we'll use new object for all API calls
    # #######################################################################
    rest = LoginHelper(module)

    # #######################################################################
    # call our login function, passing it our resources dictionary
    # #######################################################################
    first_token = first_login(module, rest)
    second_token = second_login(module, rest, first_token["id_token"])
    id_token = second_token["id_token"]
    module.exit_json(changed=True, data=id_token)

def main():
    # #######################################################################
    # we're taking in the Module's argument spec from the LoginHelper and
    #   saving it as a new object named 'argument_spec'.
    # another object is created, this time to the specification defined by
    #   the offical AnsibleModule class, and we pass in the argument_spec.
    #   this act creates our new 'module' object, which is then passed
    #   through our other, much larger, function named 'core'
    # #######################################################################
    argument_spec = LoginHelper.login_spec()
    module = AnsibleModule(argument_spec=argument_spec)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
