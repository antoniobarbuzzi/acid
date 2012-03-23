#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import abstracthandler

class NullHandler(abstracthandler.AbstractHandler):
    def __init__(self, section_name, verbose=False, dry_run=False):
        abstracthandler.AbstractHandler.__init__(self, section_name, verbose=verbose, dry_run=dry_run)
    
    def runtask(self, name, confsection):
        pass
    
