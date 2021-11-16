"""Tasks for use with Invoke.

(c) 2021 Calvin Remsburg
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from invoke import task

### ---------------------------------------------------------------------------
### DOCKER PARAMETERS
### ---------------------------------------------------------------------------
DOCKER_IMG = "registry.gitlab.com/cremsburg/ansible-collection-builder"
DOCKER_TAG = "sdcloud.0.2"

### ---------------------------------------------------------------------------
### ANSIBLE GALAXY PARAMETERS
### ---------------------------------------------------------------------------
GALAXY_KEY = os.getenv("GALAXY_KEY", "")
COLLECTION_PACKAGE = "cremsburg-sdcloud-0.0.2.tar.gz"

### ---------------------------------------------------------------------------
### CICD PARAMETERS
### ---------------------------------------------------------------------------
CICD_USERNAME = os.getenv("CICD_USERNAME", "")
CICD_PASSWORD = os.getenv("CICD_PASSWORD", "")

### ---------------------------------------------------------------------------
### SECURITY DIRECTOR CLOUD LOGIN PARAMETERS
### ---------------------------------------------------------------------------
SDCLOUD_USERNAME = os.getenv("SDCLOUD_USERNAME", "")
SDCLOUD_PASSWORD = os.getenv("SDCLOUD_PASSWORD", "")

### ---------------------------------------------------------------------------
### SYSTEM PARAMETERS
### ---------------------------------------------------------------------------
PWD = os.getcwd()

### ---------------------------------------------------------------------------
### DOCKER CONTAINER BUILD
### ---------------------------------------------------------------------------
@task
def build(context):
    # Build our docker image
    context.run(
        f"docker build -t {DOCKER_IMG}:{DOCKER_TAG} docker/",
    )

### ---------------------------------------------------------------------------
### COLLECTIONS BUILD
### ---------------------------------------------------------------------------
@task
def collection(context):
    # Build our collections package
    print("Building Ansible Galaxy Collection within container")
    context.run(
        f"docker run \
            -it \
            --rm \
            -v {PWD}/cremsburg/sdcloud:/home/sdcloud \
            -w /home/sdcloud/ \
            {DOCKER_IMG}:{DOCKER_TAG} \
            ansible-galaxy collection build --force",
        pty=True,
    )

### ---------------------------------------------------------------------------
### COLLECTIONS PUBLISH
### ---------------------------------------------------------------------------
@task
def publish(context):
    # Publish our collections package
    print("Publish our Ansible Galaxy Collection within container")
    context.run(
        f"docker run \
            -it \
            --rm \
            -v {PWD}/cremsburg/sdcloud:/home/sdcloud \
            -w /home/sdcloud/ \
            {DOCKER_IMG}:{DOCKER_TAG} \
            ansible-galaxy collection publish ./{COLLECTION_PACKAGE} --api-key={GALAXY_KEY}",
        pty=True,
    )


### ---------------------------------------------------------------------------
### DOCKER CONTAINER SHELL
### ---------------------------------------------------------------------------
@task
def shell(context):
    # Get access to the BASH shell within our container
    print("Jump into a container")
    context.run(
        f"docker run -it --rm \
            -v {PWD}/cremsburg/sdcloud:/home/sdcloud \
            -w /home/sdcloud/ \
            {DOCKER_IMG}:{DOCKER_TAG} /bin/bash",
        pty=True,
    )


### ---------------------------------------------------------------------------
### TESTS
### ---------------------------------------------------------------------------
@task
def test(context):
    # Get access to the BASH shell within our container
    print("Test the build process")
    context.run(
        f"docker run -it --rm \
            -v {PWD}/cremsburg/sdcloud:/home/sdcloud \
            -w /home/sdcloud/ \
            --env-file secrets.env \
            {DOCKER_IMG}:{DOCKER_TAG} sh tests/build.sh",
        pty=True,
    )
