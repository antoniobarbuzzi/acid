#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Antonio Barbuzzi"
__copyright__ = "Copyright (C) 2012 Antonio Barbuzzi"
__license__ = "GPLv3"
__version__ = "0.1"

import functools
import urllib
import configobj
import fabric
import fabric.tasks



from lrucache import lru_cache

def setup_fabric():
    fabric.state.env.skip_on_failure = True
    fabric.state.env.preconnect = True
    fabric.state.env.skip_bad_hosts = True
    fabric.state.env.connection_attempts = 3
    fabric.state.env.pool_size = 10
    fabric.state.env.parallel = True
    #fabric.state.env.deploy_user='hadoop' #FIXME
    fabric.state.output.debug = False
    fabric.state.output.running = False

setup_fabric()

class InvalidConfigurationFile(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class AbstractHandler(object):
    def __init__(self, section_name, dry_run):
        self.section_name = section_name
        self.dry_run = dry_run
        
    @lru_cache(maxsize=20)
    def get_machines(self, uri):
        machines = []
        for line in urllib.urlopen(uri):
            line = line.strip()
            if line and not line.startswith("#"):
                machines.append(line)
        return machines

    def validate_conf(self, subsection_name, subsection_conf):
        # Override this
        self.get_machines(subsection_conf["machines"])
    
    def validate_configuration(self, option, value):
        # Do not ovverride
        AbstractHandler.validate_conf(self, option, value)
        self.validate_conf(option, value)
    
    def execute(self, subsection_name, subsection_conf):
        if isinstance(subsection_conf, configobj.Section):
            self.init(subsection_name, subsection_conf)
            runtask = functools.partial(self.runtask, subsection_name, subsection_conf)
            runtask.name = "%s:%s" % (self.section_name, subsection_name)
            fabric.tasks.execute(runtask, hosts=self.get_machines(subsection_conf["machines"]))
            self.close(subsection_name, subsection_conf)
        else:
            raise InvalidConfigurationFile("Cannot use '%s = %s'" % (subsection_name, subsection_conf))

    def init(self, subsection_name, confsection):
        pass
    
    def runtask(self, subsection_name, confsection):
        raise NotImplementedError("Subclasses should implement this!")
    
    def close(self, subsection_name, confsection):
        pass


    
    