========================
cremsburg.sdcloud.device
========================

----------------------------
Onboard an existing firewall
----------------------------

device
======

This module will allow you to onboard an existing firewall within Security Director Cloud.

Feature set as of version 0.0.2:
  - Onboard an existing firewall
  - idempotent

Under construction

Example
-------

Here is a basic example of using the module to mange your resources in Security Director Cloud

.. code-block:: yaml

    ---
    ### #################################################################
    ### # ONBOARD AN EXISTING FIREWALL
    ### #################################################################
      - hosts: localhost
        gather_facts: False
        become: False
        tasks:
            - name: "### ONBOARD EXISTING FIREWALL"
              cremsburg.sdcloud.device:

                # define Security Director Cloud parameters
                server: "sdcloud-eap.juniperclouds.net"
                api_token: "{{ api_token.data }}"

                # define request
                host_name: "{{ host_name }}"
                cluster_type: "{{ cluster_type }}"

                # define to delete or create
                state: present
              register: firewall

Data Model
----------

If you'd like to see the options available for you within the module, have a look at the data model provided below. 

.. code-block:: python

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
