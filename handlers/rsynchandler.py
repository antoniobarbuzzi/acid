#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import abstracthandler
import fabric.api
import fabric.contrib.project 


class RsyncHandler(abstracthandler.AbstractHandler):
    def __init__(self, verbose=False, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="RSYNC", verbose=False, dry_run=dry_run)
    
    def validate_conf(self, name, confsection):
        source_dir = confsection["source_dir"] + "/"
        remote_dir = confsection["remote_dir"] + "/"        
        user = confsection["user"]

    
    def runtask(self, option, confsection):
        source_dir = confsection["source_dir"] + "/"
        remote_dir = confsection["remote_dir"] + "/"        
        user = confsection["user"]
        
        with fabric.api.settings(user=user):
            if self.verbose:
                extra_opts = "-v"
            else:
                extra_opts = "-q"
            if not self.dry_run:
                fabric.contrib.project.rsync_project(remote_dir=remote_dir, local_dir=source_dir, extra_opts=extra_opts)

