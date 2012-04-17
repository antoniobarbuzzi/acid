#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import *
from fabric.utils import warn
from fabric.contrib.files import exists

import paramiko
import socket
import hashlib

from memoize import memoized


__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

def mayfailrun(cmd, *args, **kwargs):
    with settings(warn_only=True):
        res = run(cmd, *args, **kwargs)
    return res

def adduser(username, password=None, home=None, gecos=None, shell="/bin/bash"):
    if not home:
        home="/home/%s" % username
    if not gecos:
        gecos="User %s" % username
    with settings(user="root"):
        if mayfailrun("getent passwd {username}".format(username=username)).failed:
            cmd = 'adduser --disabled-password --home {home} --gecos "{gecos}" --shell {shell} {username}'.format(home=home, gecos=gecos, shell=shell, username=username)
            run(cmd)
            if password:
                run('echo "{username}:{password}" | chpasswd'.format(username=username, password=password))

def aptkey(keyID, localFilename):
    if mayfailrun("apt-key list | grep  -q {keyID}".format(keyID=keyID)).failed:
        f = localFilename.split("/")[-1]
        put(localFilename, "/tmp/%s" % f)
        run("apt-key add /tmp/%s" % f)

class hostUp(object):    
    def __init__(self, f):
        self.f = f
        self.unreachable_machines = []
    
    def is_host_up(self, host, port):
        # Set the timeout
        original_timeout = socket.getdefaulttimeout()
        new_timeout = 3
        socket.setdefaulttimeout(new_timeout)
        host_status = False
        try:
            transport = paramiko.Transport((host, port))
            host_status = True
        except:
            pass
        #print('***Warning*** Host {host} on port {port} is down.'.format(host=host, port=port))
        socket.setdefaulttimeout(original_timeout)
        return host_status
        
    def __call__(self, *args, **kwargs):
        if self.is_host_up(env.host, int(env.port)) is False:
            warn('Host {host} on port {port} is down - Not calling "{func}" for it'.format(host=env.host, port=env.port, func=self.f.__name__))
            self.unreachable_machines.append((env.host, env.port))
        else:
            self.f(*args, **kwargs)


def debIsInstalled(progName):
    with settings(warn_only=True):
        res = run("dpkg -s %s > /dev/null" % progName)
        return res.succeeded
        
def installPackage(progName):
    if not packageIsInstalled(progName):
        run("apt-get -q -y install %s" % progName)
    
def __remoteMD5( filename):
    res = run("md5sum %s" % filename)
    return res.split()[0]

@memoized
def __localMD5( filename):
    print "Calculate MD5 for %s" % filename
    m = hashlib.md5()
    with open(filename, "rb") as f:
        chunk = f.read(8192)
        while chunk != "":        
            m.update(chunk)
            chunk = f.read(8192)
    return m.hexdigest()
    
def filesEquals( localFile, remoteFile):
    md5_a = __localMD5(localFile)
    md5_b = __remoteMD5(remoteFile)
    return md5_a == md5_b

def put_if_different(local, remote, *args, **kwargs):
    if not exists(remote) or not filesEquals(local, remote):
        put(local, remote, *args, **kwargs)
        return True
    return False

