bslicer
=======

BTRFS subvolume manipulation tool in pure python

##NAME
     bslicer : pure python subvolume/snapshot manipulation tools

##SYNOPSIS
     rsnap source_subvol_name [ destination_subvol_name ]

##DESCRIPTION
    rsnap will list `source_subvol_name`'s subvolumes structure and, if
    supplied, send to `destination_subvol_name` using btrfs send and receive.

    both souce and destination should be declared in settings.conf

###Bonnus
    other tools to create/delete snapshot, change read/write flag etc ...

##BUGS
    There's many, don't expect it work for you.

#LICENSE
  Copyright 2014 by juju2013
  This software is protected by BSD new-style licence
  Please see LICENSE for detail


