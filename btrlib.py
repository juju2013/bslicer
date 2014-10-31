#! /usr/bin/env python

import re, os, subprocess as sb
from attrdict import AttrDict
import config

cmds=config.cmds()

class btrfs:
    def __init__(self, path='/'):
        self.home=os.path.abspath(path)
        self.version=self.version()
        #--- make sur home is a subvolume
        if len(self.getObject()) < 1:
            raise ValueError("Not a rfs subvolume: %s"%path)
            return
        self.volid=self.exec(['inspect','rootid',path]).split('\n')[0]
        self.tree={}
        self.buildTree(self.home)

    def version(self):
        return self.exec(['version']).split('\n')[0].split(' ')[1][1:]

    def rootid(self, path=None):
        path = path or self.home
        return self.exec(['inspect-internal','rootid', path]).split('\n')[0]

    def buildTree(self, path=None):
        path = path or self.home
        res={'5':AttrDict({"parent":'5',"children":[],"path":"<root>"})}
        #--- build elements
        for r in self.exec(['sub','list','-p','-a','-c','-g','-t','--sort=path',path]).split('\n')[2:]:
            try:
                (volid, gen, cgen, parent, top, filer1, path)=r.split('\t')
                mounted = not path.startswith('<FS_TREE>')
                if not mounted :
                    path = path[9:]
                res[volid] = {
                        "gen":gen,
                        "cgen":cgen,
                        "parent":parent,
                        "top":top,
                        "path":path[1:] if path.startswith('/') else path,
                        "fspath": None if volid != self.volid else self.home,
                        "mounted": mounted,
                        "children":[]
                        }
            except Exception as err:
                #print('%s: %s'%(err,r))
                continue
        res[self.volid]['fspath']=self.home
        #--- build tree
        self.tree=res
        r=re.compile("^%s/(.*)$"%res[self.volid]['path'])
        for volid, attr in self.tree.items():
            p=attr['parent']
            rs = r.match(attr['path'])
            if rs:
                self.tree[volid]['fspath']=os.path.join(self.home,rs.group(1))
            if volid != p:
                self.tree[p]['children'].append(volid)
        return self.tree

    def getObject(self, path=None):
        path = path or self.home
        attrs={}
        for r in self.exec(['sub', 'show', path ]).split('\n')[1:]:
            try:
                attr, val = r.strip().split(':',1)
                attrs[attr]=val.strip()
            except:
                # print("error passing:%s"%r)
                continue
        return attrs

    def getVolid(self, path=None):
        path =path or self.home
        return self.getObject(path)['Object ID']

    def subTree(self, volid=None, tree={}):
        volid = volid or self.volid
        atr=self.tree[volid]
        tree[volid]=atr
        for i in atr['children']:
            tree=self.subTree(i, tree)
        return tree

    def exec(self, cmd):
        cmd=cmd
        cmd.insert(0,cmds.btrfs)
        cmd.insert(0,cmds.sudo)
        return self.sysExec(cmd)

    def sysExec(self, cmd):
        return sb.check_output(cmd).decode('utf-8')

    def readOnly(self, volid=None):
        self.setProperty(True, volid)

    def readWrite(self, volid=None):
        self.setProperty(False, volid)

    def setProperty(self, ro=True, volid=None):
        for i in self.walkUp(volid):
            fspath=self.tree[i]['fspath']
            if fspath:
                print("(%s)%s set to %s"%(i, fspath,'readonly' if ro else 'readwrite'))
                self.exec(['prop','set','-ts',fspath,'ro','true' if ro else 'false'])

    def sync(self):
        self.sysExec(['sync'])
        self.buildTree()

    def newVolume(self, path):
        self.exec(['sub','create', path])
        self.sync()
        return self.getVolid(path)

    def snapshotRecursive(self, volid, destination):
        rootPath=self.tree[volid]['fspath']
        if not rootPath: raise ValueError("%s outside my scope"%volid);
        rootPath=rootPath[:len(os.path.basename(rootPath))*-1 -1]
        print("rootpath is %s"%rootPath)
        for v in self.walkDown(volid):
            newPath=os.path.join(destination, self.tree[v]['fspath'][len(rootPath)+1:])
            newVolid=self.snapshot(v, newPath)
            print("Created snapshot %s -> (%s)%s"%(self.tree[v]['fspath'], newVolid, newPath))
        self.sync()


    def snapshot(self, volid, destination):
        source = self.tree[volid]['fspath']
        if source:
            # if destination exists, remove it (thus must be empty) as btrfs snap will create it
            if os.path.exists(destination):
                try:
                    os.rmdir(destination)
                except:
                    raise ValueError("%s is not empty and cannot be used as snapshot destionation"%destination)
                    return  None
                print("removed empty destination before snapshot: %s"%destination)
            res=self.exec(['sub','snapshot',source,destination]).split('\n')[0]
            x=re.match("^Create a snapshot of '(.*)' in '(.*)'$",res)
            return self.getVolid(x.group(2))
        else:
            raise ValueError("(%s)%s outside initial scope"%(volid, source))
            return None

    def deleteSnapshotRecursive(self, volid):
        for s in self.walkUp(volid):
            self.deleteSnapshot(s)
        self.sync()

    def deleteSnapshot(self, volid):
        self.exec(['sub','delete',self.tree[volid]['fspath']])

    def walkUp(self, volid=None):
        volid=volid or self.volid
        attr=self.tree[volid]
        for i in attr['children']:
            yield from self.walkUp(i)
        yield(volid)

    def walkDown(self, volid=None):
        volid=volid or self.volid
        yield(volid)
        attr=self.tree[volid]
        for i in attr['children']:
            yield from self.walkDown(i)

    def voltree(self, volid='5'):
        volid = volid or self.volid
        self.printTree(volid,'','path')

    def fstree(self, volid=None):
        volid = volid or self.volid
        self.printTree(volid,'','fspath')

    def printTree(self,volid, ident, attr):
        print("%s(%s)%s"%(ident, volid, self.tree[volid][attr]))
        for c in self.tree[volid]['children']:
            self.printTree(c, ident+'\t',attr)


