#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import abstracthandler

class PrintHandler(abstracthandler.AbstractHandler):
    def __init__(self, section_name, verbose=False):
        abstracthandler.AbstractHandler.__init__(self, section_name, verbose=verbose)
    
    def runtask(self, name, confsection):
        print "-", name
        for item in confsection.items():
            print "  ", item

