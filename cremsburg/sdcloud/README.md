# Juniper Security Director Cloud Ansible Modules

[![N|Solid](https://gitlab.com/_calvinr/brand-logos/-/raw/814574fcca406e0b5ddbff8ae558b05cd6e23c1e/text-100.jpg)](https://blogs.juniper.net/en-us/security/introducing-juniper-security-director-cloud-junipers-portal-to-sase)

## `Overview`

The goal of this collection is to provide an easier way to interact with Juniper Security Director Cloud. While nothing will stop you from using the built-in module, you may find that working with pre-packaged modules can help simplify the development of your playbook, or it may just be easier to support as a team.

## 📋 `Ansible version compatibility`

This module has been tested back to Ansible version 2.9

## ⚙️ `Batteries Included`

Here is a short list of modules included within the collection, expect feature parity with the [official Postman collection](https://documenter.getpostman.com/view/224925/SzYgQufe?version=latest#intro) before this project hits `version 1.0.0`

Name | Description
---- | -----------
[cremsburg.sdcloud.device](https://gitlab.com/_calvinr/networking/Security-Director-Cloud-Ansible-Collection/-/blob/master/cremsburg/sdcloud/docs/cremsburg.sdcloud.device.rst)|Onboard an existing firewall into SD Cloud
[cremsburg.sdcloud.login](https://gitlab.com/_calvinr/networking/Security-Director-Cloud-Ansible-Collection/-/blob/master/cremsburg/sdcloud/docs/cremsburg.sdcloud.login.rst)|Login to SD Cloud and store API token
[cremsburg.sdcloud.ztp](https://gitlab.com/_calvinr/networking/Security-Director-Cloud-Ansible-Collection/-/blob/master/cremsburg/sdcloud/docs/cremsburg.sdcloud.ztp.rst)|ZTP a new firewall

## 🚀 `Executing the playbook`

After installing the collections, you can call the modules by using their full name path.

`test.yaml`

```yaml
    ---
    ### #################################################################
    ### # LOGIN TO SECURITY DIRECTOR CLOUD
    ### #################################################################
      - hosts: localhost
        gather_facts: False
        become: False
        tasks:
            - name: "### LOGIN "
              cremsburg.sdcloud.login:

                server: "sdcloud.juniper.net"
                username: "example@juniper.net"
                password: "mysecretpassword"
                scope_id: "12345678-1234-1234-1234-123456789012"

            register: api_token

            - debug:
                var: api_token.data

            - name: "### ZTP FIREWALL"
              cremsburg.sdcloud.ztp:

                # define Security Director Cloud parameters
                server: "sdcloud-eap.juniperclouds.net"
                api_token: "{{ api_token.data }}"

                # define request
                serial: "ABCDEFG123"
                root_pwd: "juniper123"

                # define to delete or create
                state: present
              register: firewall

            - debug:
                var: firewall
```

Then simply run your playbook

```sh
ansible-playbook test.yaml
```

If you used Ansible Vault to encrypt your secrets, you need to append the `--ask-vault-pass` to your command.

## ⚠️ Very Important! ⚠️

Please make sure to manage your sensative information carfully. While the modules support the parameter of `api_key`, this should never be statically entered with your token in clear text.

Here are better alternatives:

### Manage your credientials as an environmentals

```sh
export SDCLOUD_USERNAME=myusername@juniper.net
export SDCLOUD_PASSWORD=mysupersecretpassword
export SDCLOUD_SCOPE_ID=12345678-1234-1234-1234-123456789012
export SDCLOUD_SERVER=sdcloud.juniper.net
```

### Manage your API token as a secret with Ansible Vault

create a file to store your API token in

`$ vim vault.yaml`

```yaml
api_token: "MY_SDCLOUD_API_TOKEN_HERE"
```

encrypt the new file

```sh
ansible-vault encrypt vault.yml
```

update your playbook to look for variables within this new, encrypted file

```yaml
---
- hosts: localhost
  vars_files:
    - vault.yml
  tasks:
    - name: "### LOGIN "
      cremsburg.sdcloud.login:

        server: "sdcloud.juniper.net"
        username: "example@juniper.net"
        password: "mysecretpassword"
        scope_id: "12345678-1234-1234-1234-123456789012"

    register: api_token

    - debug:
        var: api_token.data

    - name: "### ZTP FIREWALL"
      cremsburg.sdcloud.ztp:

        # define Security Director Cloud parameters
        server: "sdcloud-eap.juniperclouds.net"
        api_token: "{{ api_token.data }}"

        # define request
        serial: "ABCDEFG123"
        root_pwd: "juniper123"

        # define to delete or create
        state: present
      register: firewall

    - debug:
        var: firewall

```

and now you'll need to pass your vault password when using the playbook

```sh
ansible-playbook --ask-vault-pass test.yaml
```

## Development

Want to contribute? Great!

Submit a PR and let's work on this together :D
