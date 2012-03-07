#!/usr/bin/env python
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import abstracthandler
import fabric.api
import fabric_libs.fab_utils

class PackageHandler(abstracthandler.AbstractHandler):
    def __init__(self, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="PACKAGES", dry_run=dry_run)
    
    def validate_conf(self, name, confsection):
        pkgs = confsection.as_list("packages_list")
        
    def runtask(self, name, confsection):
        pkgs = confsection.as_list("packages_list")
        with fabric.api.settings(user="root"):
            for pkg in pkgs:
                if not self.dry_run:
                    fabric_libs.fab_utils.installPackage(pkg)
