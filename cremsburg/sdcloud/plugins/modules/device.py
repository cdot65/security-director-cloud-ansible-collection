#!/usr/bin/python

# Copyright: (c) 2020, Calvin Remsburg (@cremsburg) <cremsburg@protonmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: device

short_description: Manage a firewall within Security Director Cloud.

version_added: "0.0.2"

description: This module will leverage Security Director Cloud's REST API to automate the management of firewalls.

options:
    api_token:
        description:
          - used to authenticate to the API
        required: true
        type: str
    host_name:
        description:
          - device's hostname
        required: True
        type: str
    cluster_type:
        required=True,
        choices:
          - 'cluster'
          - 'standalone'
          - 'CHASSIS_CLUSTER'
          - 'STANDALONE'
        type='str'
    server:
        description:
          - Security Director Cloud URL
        required: true
        type: str
    state:
        description:
          - declare whether you want the resource to exist or be deleted
        required: true
        choices:
          - 'absent'
          - 'present'
        type: str
    validate_certs:
        description:
          - whether or not the certificate is valid
          - may help those behind proxies
        required: false
        default: true
        type: bool

extends_documentation_fragment:
    - cremsburg.sdcloud.device

author:
    - Calvin Remsburg (@cremsburg)
'''

EXAMPLES = r'''
---
### #################################################################
### # ONBOARD AN EXISTING FIREWALL
### #################################################################
- hosts: localhost
  gather_facts: False
  become: False
  tasks:
    - name: "### ZTP FIREWALL cicd-firewall"
      cremsburg.sdcloud.device:

        # define Security Director Cloud parameters
        server: "sdcloud-eap.juniperclouds.net"
        api_token: "{{ api_token }}"

        # define request
        host_name: "juniper-srx-fw0"
        cluster_type: "standalone"

        # define to delete or create
        state: present
      register: firewall

    - debug:
        var: firewall
'''


from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cremsburg.sdcloud.plugins.module_utils.sdcloud.api import SDCloudHelper
from ansible.module_utils._text import to_native


def manage_device(resources, module, rest):
    # ########################################################################
    # we need to see if our firewall has already been created, this determines
    #   our future API calls.
    # we create a new dictionary with a k/v of 'provisioned' set to False.
    #   if the device had already been provisioned, we'll flip this bit to True
    #   and store it's host_name and UUID
    # ########################################################################
    firewall_element = dict()
    firewall_element['provisioned'] = False
    for each in resources["device-view"]:
        if each['system_info']['host_name'] == module.params['host_name']:
            firewall_element['uuid'] = each['uuid']
            firewall_element['host_name'] = each['system_info']['host_name']
            firewall_element['provisioned'] = True

    # #######################################################################
    # if the user set the state to 'absent', then we need to either delete
    #   an existing device, or report back to the user that the device didn't
    #   exist.
    # #######################################################################
    if module.params['state'] == "absent":
        if firewall_element['provisioned'] is True:
            response = rest.post(f"deviceonboarding/remove-devices", data={
                "device_info": [
                    {
                        "device_uuid": firewall_element['uuid'],
                        "device_name": firewall_element['host_name']
                    }
                ],
                "force_delete": False
            })
            module.exit_json(changed=True, data=response.json)
        else:
            module.exit_json(changed=False, data="Device does not exist, exiting")

    # #######################################################################
    # looking to either create a device or skip the process
    # #######################################################################
    else:

        # #######################################################################
        # create the device in Security Director Cloud if it doesn't exist
        # #######################################################################
        if firewall_element['provisioned'] is False:

            # ###########################################################################
            # firewall_element_data: parameters entered by the user to create the resource
            # ###########################################################################
            firewall_element_data = dict()
            firewall_element_data['device_info'] = list()
   
            firewall_element_data['activation_type'] = 'MANUAL'
            firewall_element_data['device_info'].append(
                {
                    'device': {
                        'name': module.params['host_name'],
                        'device_family_name': 'juniper-srx',
                        'system_info': {
                            'cluster_type': module.params['cluster_type'],
                            'host_name': module.params['host_name']
                        },
                        'DeviceProperties': [
                            {
                                'Name': 'DISCOVERY_TYPE',
                                'Value': 'NON-ZTP'
                            }
                        ]
                    }
                }
            )

            # ###########################################################################
            # make the API call and store the output in a variable named response
            # ###########################################################################
            response = rest.post("devicemanager/add-devices", data=firewall_element_data)

            module.exit_json(changed=True, data=response.json)

        module.exit_json(changed=False, data=firewall_element)


def core(module):
    # #######################################################################
    # this is where we take in AnsibleModule class created earlier in the
    # main function, when we inserted our argument spec into it.
    # we'll use new object for all API calls
    # #######################################################################
    rest = SDCloudHelper(module)

    # #######################################################################
    # gather a list of firewalls already created within SD Cloud
    # make sure the status code received was a 200
    # #######################################################################
    response = rest.get(f"devicemodel/device-view")
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to receive a response from the API, here is the response information to help you debug : {response.info}")

    resources = response.json

    # #######################################################################
    # validate that resources is a dictionary
    # #######################################################################
    if isinstance(resources, dict):
        pass
    else:
        module.fail_json(msg=f"The response returned is not in a dictionary format, contact support \n{resources}")

    # #######################################################################
    # call our manage_device function, passing it our resources dictionary
    # #######################################################################
    manage_device(resources, module, rest)

    # #######################################################################
    # safely exit if manage_device isn't executed, will return resources
    # #######################################################################
    module.exit_json(changed=False, data=resources)


def main():
    # #######################################################################
    # this is the main function, did the name give it away?
    # we're taking in the Module's argument spec from the SDCloudHelper and
    #   saving it as a new object named 'argument_spec'.
    # another object is created, this time to the specification defined by
    #   the offical AnsibleModule class, and we pass in the argument_spec.
    #   this act creates our new 'module' object, which is then passed
    #   through our other, much larger, function named 'core'
    # #######################################################################
    argument_spec = SDCloudHelper.device_spec()
    module = AnsibleModule(argument_spec=argument_spec)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
