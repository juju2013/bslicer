#! /usr/bin/env python

# Copyright 2014 by juju2013
# This software is protected by BSD new-style licence
# Please see LICENSE for detail

import yaml
from attrdict import AttrDict

class config:
    def __init__(self, cfile='settings.conf'):
        with open(cfile) as f:
            self.conf=AttrDict(yaml.safe_load(f))


commands="""
ls:
  /usr/bin/ls
btrfs:
  /usr/bin/btrfs
sudo:
  /usr/sbin/sudo
"""

def cmds():
    return AttrDict(yaml.load(commands))
