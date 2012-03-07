#!/usr/bin/env python
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

﻿#from fabric.api import run, env
from fabric.api import *
from fabric.decorators import with_settings
from fabric.context_managers import cd
from fabric.contrib.files import append

from fab_utils import mayfailrun, put_if_different



class GitConf(object):
    #TODO rename directory in confDirectory
    def __init__(self, repositoryURL, directory, remote_user, branch="master", gitusername=None, gitpassword=None):
        self.repositoryURL = repositoryURL
        self.gitusername = gitusername
        self.gitpassword = gitpassword
        self.directory = directory
        self.remote_user = remote_user
        self.branch = branch
    
    def propagateKey(self, key_filename, cert_filename=None, destination="~/.ssh/"):
        with settings(user=self.remote_user):
            mayfailrun("mkdir -p %s" % destination)
            _destination = "%s/id_dsa" % (destination)
            put_if_different(key_filename, _destination, mode=0600)
            if cert_filename is None:
                cert_filename = "%s.pub" % key_filename
            put_if_different(cert_filename, "%s.pub" % _destination, mode=0644)
            #run("chown -R {user}:{user} {path}".format(user=user, path=destination))
            append("%s/config" % destination, "StrictHostKeyChecking no")
        
    def _initDirectory(self):
        with settings(user=self.remote_user):
            mayfailrun("rm -rf {directory}".format(directory=self.directory))
            run("git clone {rep} {dir}".format(rep=self.repositoryURL, dir=self.directory))
    
    def _updateDirectory(self):
        with settings(user=self.remote_user):
            with cd(self.directory):
                run('pwd')
                run('git checkout -b {branch} origin/{branch}'.format(branch=self.branch))  

    def configure(self):
        self._initDirectory()
        #FIXME it works only because I remove the conf directory every time before init
        if(self.branch != "master"):
            self._updateDirectory()
    