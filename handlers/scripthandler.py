#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import os
import abstracthandler
import fabric.tasks
import fabric.api


class ScriptHandler(abstracthandler.AbstractHandler):
    def __init__(self, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="SCRIPT", dry_run=dry_run)
    
    def validate_conf(self, name, confsection):
        user = confsection["user"]
        script = confsection["script"]

    
    def runtask(self, name, confsection):
        user = confsection["user"]
        script = confsection["script"]
        remote_script = "/tmp/" + os.path.basename(script)
        #f = urllib.urlopen(script_url)
        with fabric.api.settings(user=user):
            if not self.dry_run:
                fabric.api.put(script, remote_script)
                fabric.api.run("chmod +x %s" % remote_script)
                fabric.api.run(remote_script)
