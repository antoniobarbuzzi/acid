#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import abstracthandler

from fabric_libs.fab_gitconf import GitConf

class GitHandler(abstracthandler.AbstractHandler):
    def __init__(self, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="GIT", dry_run=dry_run)
    
    def validate_conf(self, name, confsection):
        remote_user = confsection["user"]
        remote_dir = confsection["remote_dir"]
        repository_url = confsection["url"]
        branch = confsection["branch"]        
        gitusername = confsection["gitusername"] or None
        gitpassword = confsection["gitpassword"] or None        
        ssh_key = confsection["ssh_key"]
        ssh_cert = confsection["ssh_cert"]

        
    def runtask(self, name, confsection):
        remote_user = confsection["user"]
        remote_dir = confsection["remote_dir"]
        repository_url = confsection["url"]
        branch = confsection["branch"]        
        gitusername = confsection["gitusername"] or None
        gitpassword = confsection["gitpassword"] or None        
        ssh_key = confsection["ssh_key"]
        ssh_cert = confsection["ssh_cert"]
        if not self.dry_run:
            gitconf = GitConf(repository_url, remote_dir, remote_user=remote_user, branch=branch, gitusername=gitusername, gitpassword=gitpassword)    
            gitconf.propagateKey(ssh_key, ssh_cert)
            gitconf.configure()
