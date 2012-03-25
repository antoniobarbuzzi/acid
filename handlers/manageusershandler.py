#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import abstracthandler
from fabric_libs.fab_utils import adduser

class UserHandler(abstracthandler.AbstractHandler):
    def __init__(self, verbose=False):
        abstracthandler.AbstractHandler.__init__(self, section_name="USERS", verbose=verbose)
    
    def validate_conf(self, name, confsection):
        user=confsection["user"]
        password=confsection["password"]
        home=confsection["home"]
        gecos=confsection["gecos"]
        shell=confsection["shell"]

    
    def runtask(self, name, confsection):
        user=confsection["user"]
        password=confsection["password"]
        home=confsection["home"]
        gecos=confsection["gecos"]
        shell=confsection["shell"]
        adduser(user, password, home, gecos, shell)
