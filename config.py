#! /usr/bin/env python

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
