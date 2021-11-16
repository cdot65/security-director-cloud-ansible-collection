=====================
cremsburg.sdcloud.ztp
=====================

-------------------------
ZTP a new firewall device
-------------------------

ztp
======

This module will allow you to ZTP a new firewall within Security Director Cloud.

Feature set as of version 0.0.1:
  - ZTP a new firewall
  - idempotent

Under construction

Example
-------

Here is a basic example of using the module to mange your resources in Security Director Cloud

.. code-block:: yaml

    ---
    ### #################################################################
    ### # ZTP A NEW FIREWALL
    ### #################################################################
      - hosts: localhost
        gather_facts: False
        become: False
        tasks:
            - name: "### ZTP FIREWALL cicd-firewall"
              cremsburg.sdcloud.ztp:

                # define Security Director Cloud parameters
                server: "sdcloud-eap.juniperclouds.net"
                api_token: "{{ api_token }}"

                # define request
                serial: "ABCDEFG123"
                root_pwd: "juniper123"

                # define to delete or create
                state: present
              register: firewall

            - debug:
                var: firewall

Data Model
----------

If you'd like to see the options available for you within the module, have a look at the data model provided below. 

.. code-block:: python

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

