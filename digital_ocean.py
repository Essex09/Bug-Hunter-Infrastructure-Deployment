#!/usr/bin/env python

"""
DigitalOcean external inventory script
======================================

Generates Ansible inventory of DigitalOcean Droplets.

In addition to the --list and --host options used by Ansible, there are options
for generating JSON of other DigitalOcean data.  This is useful when creating
droplets.  For example, --regions will return all the DigitalOcean Regions.
This information can also be easily found in the cache file, whose default
location is /tmp/ansible-digital_ocean.cache).

The --pretty (-p) option pretty-prints the output for better human readability.

----
Although the cache stores all the information received from DigitalOcean,
the cache is not used for current droplet information (in --list, --host,
--all, and --droplets).  This is so that accurate droplet information is always
found.  You can force this script to use the cache with --force-cache.

----
Configuration is read from `digital_ocean.ini`, then from environment variables,
and then from command-line arguments.

Most notably, the DigitalOcean API Token must be specified. It can be specified
in the INI file or with the following environment variables:
    export DO_API_TOKEN='abc123' or
    export DO_API_KEY='abc123'

Alternatively, it can be passed on the command-line with --api-token.

If you specify DigitalOcean credentials in the INI file, a handy way to
get them into your environment (e.g., to use the digital_ocean module)
is to use the output of the --env option with export:
    export $(digital_ocean.py --env)

----
The following groups are generated from --list:
 - ID    (droplet ID)
 - NAME  (droplet NAME)
 - digital_ocean
 - image_ID
 - image_NAME
 - distro_NAME  (distribution NAME from image)
 - region_NAME
 - size_NAME
 - status_STATUS

For each host, the following variables are registered:
 - do_backup_ids
 - do_created_at
 - do_disk
 - do_features - list
 - do_id
 - do_image - object
 - do_ip_address
 - do_private_ip_address
 - do_kernel - object
 - do_locked
 - do_memory
 - do_name
 - do_networks - object
 - do_next_backup_window
 - do_region - object
 - do_size - object
 - do_size_slug
 - do_snapshot_ids - list
 - do_status
 - do_tags
 - do_vcpus
 - do_volume_ids

-----
```
usage: digital_ocean.py [-h] [--list] [--host HOST] [--all] [--droplets]
                        [--regions] [--images] [--sizes] [--ssh-keys]
                        [--domains] [--tags] [--pretty]
                        [--cache-path CACHE_PATH]
                        [--cache-max_age CACHE_MAX_AGE] [--force-cache]
                        [--refresh-cache] [--env] [--api-token API_TOKEN]

Produce an Ansible Inventory file based on DigitalOcean credentials

optional arguments:
  -h, --help            show this help message and exit
  --list                List all active Droplets as Ansible inventory
                        (default: True)
  --host HOST           Get all Ansible inventory variables about a specific
                        Droplet
  --all                 List all DigitalOcean information as JSON
  --droplets, -d        List Droplets as JSON
  --regions             List Regions as JSON
  --images              List Images as JSON
  --sizes               List Sizes as JSON
  --ssh-keys            List SSH keys as JSON
  --domains             List Domains as JSON
  --tags                List Tags as JSON
  --pretty, -p          Pretty-print results
  --cache-path CACHE_PATH
                        Path to the cache files (default: .)
  --cache-max_age CACHE_MAX_AGE
                        Maximum age of the cached items (default: 0)
  --force-cache         Only use data from the cache
  --refresh-cache, -r   Force refresh of cache by making API requests to
                        DigitalOcean (default: False - use cache files)
  --env, -e             Display DO_API_TOKEN
  --api-token API_TOKEN, -a API_TOKEN
                        DigitalOcean API Token
```

"""

# (c) 2013, Evan Wies <evan@neomantra.net>
# (c) 2017, Ansible Project
# (c) 2017, Abhijeet Kasurde <akasurde@redhat.com>
#
# Inspired by the EC2 inventory plugin:
# https://github.com/ansible/ansible/blob/devel/contrib/inventory/ec2.py
#
# This file is part of Ansible,
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

######################################################################

import argparse
import ast
import os
import re
import requests
import sys
from time import time

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import json


class DoManager:
    def __init__(self, api_token):
        self.api_token = api_token
        self.api_endpoint = 'https://api.digitalocean.com/v2'
        self.headers = {'Authorization': 'Bearer {0}'.format(self.api_token),
                        'Content-type': 'application/json'}
        self.timeout = 60

    def _url_builder(self, path):
        if path[0] == '/':
            path = path[1:]
        return '%s/%s' % (self.api_endpoint, path)

    def send(self, url, method='GET', data=None):
        url = self._url_builder(url)
        data = json.dumps(data)
        try:
            if method == 'GET':
                resp_data = {}
                incomplete = True
                while incomplete:
                    resp = requests.get(url, data=data, headers=self.headers, timeout=self.timeout)
                    json_resp = resp.json()

                    for key, value in json_resp.items():
                        if isinstance(value, list) and key in resp_data:
                            resp_data[key] += value
                        else:
                            resp_data[key] = value

                    try:
                        url = json_resp['links']['pages']['next']
                    except KeyError:
                        incomplete = False

        except ValueError as e:
            sys.exit("Unable to parse result from %s: %s" % (url, e))
        return resp_data

    def all_active_droplets(self):
        resp = self.send('droplets/')
        return resp['droplets']

    def all_regions(self):
        resp = self.send('regions/')
        return resp['regions']

    def all_images(self, filter_name='global'):
        params = {'filter': filter_name}
        resp = self.send('images/', data=params)
        return resp['images']

    def sizes(self):
        resp = self.send('sizes/')
        return resp['sizes']

    def all_ssh_keys(self):
        resp = self.send('account/keys')
        return resp['ssh_keys']

    def all_domains(self):
        resp = self.send('domains/')
        return resp['domains']

    def show_droplet(self, droplet_id):
        resp = self.send('droplets/%s' % droplet_id)
        return resp['droplet']

    def all_tags(self):
        resp = self.send('tags')
        return resp['tags']


class DigitalOceanInventory(object):

    ###########################################################################
    # Main execution path
    ###########################################################################

    def __init__(self):
        """Main execution path """

        # DigitalOceanInventory data
        self.data = {}  # All DigitalOcean data
        self.inventory = {}  # Ansible Inventory

        # Define defaults
        self.cache_path = '.'
        self.cache_max_age = 0
        self.use_private_network = False
        self.group_variables = {}

        # Read settings, environment variables, and CLI arguments
        self.read_settings()
        self.read_environment()
        self.read_cli_args()

        # Verify credentials were set
        if not hasattr(self, 'api_token'):
            msg = 'Could not find values for DigitalOcean api_token. They must be specified via either ini file, ' \
                  'command line argument (--api-token), or environment variables (DO_API_TOKEN)\n'
            sys.stderr.write(msg)
            sys.exit(-1)

        # env command, show DigitalOcean credentials
        if self.args.env:
            print("DO_API_TOKEN=%s" % self.api_token)
            sys.exit(0)

        # Manage cache
        self.cache_filename = self.cache_path + "/ansible-digital_ocean.cache"
        self.cache_refreshed = False

        if self.is_cache_valid():
            self.load_from_cache()
            if len(self.data) == 0:
                if self.args.force_cache:
                    sys.stderr.write('Cache is empty and --force-cache was specified\n')
                    sys.exit(-1)

        self.manager = DoManager(self.api_token)

        # Pick the json_data to print based on the CLI command
        if self.args.droplets:
            self.load_from_digital_ocean('droplets')
            json_data = {'droplets': self.data['droplets']}
        elif self.args.regions:
            self.load_from_digital_ocean('regions')
            json_data = {'regions': self.data['regions']}
        elif self.args.images:
            self.load_from_digital_ocean('images')
            json_data = {'images': self.data['images']}
        elif self.args.sizes:
            self.load_from_digital_ocean('sizes')
            json_data = {'sizes': self.data['sizes']}
        elif self.args.ssh_keys:
            self.load_from_digital_ocean('ssh_keys')
            json_data = {'ssh_keys': self.data['ssh_keys']}
        elif self.args.domains:
            self.load_from_digital_ocean('domains')
            json_data = {'domains': self.data['domains']}
        elif self.args.tags:
            self.load_from_digital_ocean('tags')
            json_data = {'tags': self.data['tags']}
        elif self.args.all:
            self.load_from_digital_ocean()
            json_data = self.data
        elif self.args.host:
            json_data = self.load_droplet_variables_for_host()
        else:    # '--list' this is last to make it default
            self.load_from_digital_ocean('droplets')
            self.build_inventory()
            json_data = self.inventory

        if self.cache_refreshed:
            self.write_to_cache()

        if self.args.pretty:
            print(json.dumps(json_data, indent=2))
        else:
            print(json.dumps(json_data))

    ###########################################################################
    # Script configuration
    ###########################################################################

    def read_settings(self):
        """ Reads the settings from the digital_ocean.ini file """
        config = ConfigParser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'digital_ocean.ini')
        config.read(config_path)

        # Credentials
        if config.has_option('digital_ocean', 'api_token'):
            self.api_token = config.get('digital_ocean', 'api_token')

        # Cache related
        if config.has_option('digital_ocean', 'cache_path'):
            self.cache_path = config.get('digital_ocean', 'cache_path')
        if config.has_option('digital_ocean', 'cache_max_age'):
            self.cache_max_age = config.getint('digital_ocean', 'cache_max_age')

        # Private IP Address
        if config.has_option('digital_ocean', 'use_private_network'):
            self.use_private_network = config.getboolean('digital_ocean', 'use_private_network')
