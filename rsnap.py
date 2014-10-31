#! /usr/bin/env python

import sys, os, subprocess as sb
from config import config,cmds
import btrlib, imp

cmds=cmds()

def rbackup(source='source', destination='destination'):
    conf=config().conf
    conf['source']=conf[source]
    conf['destination']=conf[destination]
    srcRoot=conf.source.path
    dstRoot=conf.destination.path
    baseName=os.path.basename(srcRoot)
    src=btrlib.btrfs(srcRoot)
    dh=''
    try:dstCmd=conf.destination.rssh.split(' ')
    except:dstCmd=['sh','-c']
    #--- create destionation subvolume
    tcmd=dstCmd[:]
    tcmd.append('sudo btrfs sub create "%s"'%dstRoot)
    try:sb.check_output(tcmd)
    except:pass
    for v in src.walkDown():
        s=src.tree[v]['fspath']
        d=os.path.dirname(os.path.join(dstRoot,dh,s[len(srcRoot)+1:]))
        rCmd=dstCmd[:]
        rCmd.append('%s "%s"'%(conf.destination.rcmd, d))
        print("sending '%s' --> '%s'"%(s,d))
        sbSend=sb.Popen([cmds.sudo, cmds.btrfs,'send','-v',s],stdout=sb.PIPE)
        sbReceive=sb.Popen(rCmd, stdin=sbSend.stdout, stdout=sb.PIPE)
        out,err = sbReceive.communicate()
        tcmd=dstCmd[:]
        tcmd.append('sudo btrfs property set -ts "%s" ro false'%os.path.join(d,os.path.basename(s)))
        try:sb.check_output(tcmd)
        except:pass
        dh=baseName


def test(path='/'):
    imp.reload(btrlib)
    b=btrlib.btrfs(path)
    return b

def main():
    print("Btrfs Slicer")
    conf=config().conf
    b=test('/mnt' if len(sys.argv)<2 else conf[sys.argv[1]]['path'])
    print("btrfs version %s"%b.version)
    b.fstree()
    if len(sys.argv)==3: rbackup(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
